from fastapi import HTTPException,status,Depends
from sqlalchemy import select,update,or_,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.article import ArticleCreate,ArticleQuery,ArticleUpdate
from app.utils.depends import PaginateParams
from app.utils.enum import CommonOrderBy,ArticleStatus

from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag,article_tags
from app.models.like import Like

from app.services.tag import TagService
from app.services.category import CategoryService

class ArticleService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.tagService = TagService(db)
        self.categoryService = CategoryService(db)

    async def get_by_id(self,article_id:int):
        result = await self.db.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()
    
    async def get_list(self,paginateParams:PaginateParams,data:ArticleQuery):
        size = paginateParams.size
        offset = paginateParams.offset

        query = (
            select(Article)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.author)
            )
        )
        total_query = select(func.count(Article.id))
        if data.status:
            query = query.where(Article.status == data.status)
            total_query = total_query.where(Article.status == data.status)

        if data.category_id:
            print("category_id")
            query = query.where(Article.category_id == data.category_id)
            total_query = total_query.where(Article.category_id == data.category_id)

        if data.author_id:
            query = query.where(Article.author_id == data.author_id)
            total_query = total_query.where(Article.author_id == data.author_id)

        if data.q:
            q = f"%{data.q}%"
            query = query.where(
                or_(
                    Article.title.like(q),
                    Article.content.like(q),
                    Article.summary.like(q)
                )
            )
            total_query = total_query.where(
                or_(
                    Article.title.like(q),
                    Article.content.like(q),
                    Article.summary.like(q)
                )
            )

        if data.tag_id:
            query = query.join(article_tags, Article.id == article_tags.c.article_id).where(article_tags.c.tag_id == data.tag_id)
            total_query = total_query.join(article_tags, Article.id == article_tags.c.article_id).where(article_tags.c.tag_id == data.tag_id)

        sort_column = getattr(Article, data.sort_by, Article.created_at)
        if data.order == CommonOrderBy.ASC:
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        total = await self.db.execute(total_query)
        total = total.scalar_one() or 0

        if total is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据为空"
            )

        query = query.offset(offset).limit(size)
        results = await self.db.execute(query)
        result = results.scalars().all()
        return total,result

    async def create(self,user:User,data:ArticleCreate):
        category = await self.categoryService.get_by_id(data.category_id)
        if not category:
            raise ValueError(f"分类 ID {data.category_id} 不存在")
        
        # 2. 验证标签是否存在
        tags = []
        if data.tag_ids:
            tags = await self.tagService.get_by_ids(data.tag_ids)
            if len(tags) != len(data.tag_ids):
                raise ValueError("部分标签不存在")

        article = Article(
            title=data.title,
            content=data.content,
            summary=data.summary,
            category_id=data.category_id,
            is_private=data.is_private,
            author_id=user.id,
            status=data.status,  # 确保有默认值
        )
        # 4. 关联标签
        if tags:
            article.tags = list(tags)  # ✅ 直接赋值关联对象列表
        # 5. 保存
        self.db.add(article)
        await self.db.commit()
    
        # 6. 重新查询完整数据（预加载关联关系）
        stmt = (
            select(Article)
            .where(Article.id == article.id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.author)
            )
        )
        result = await self.db.execute(stmt)
        
        return result.scalar_one_or_none()
    
    async def detail(self,article_id:int):
        if not await self.get_by_id(article_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,\
                detail="文章ID不存在"
            )
        query = (
            select(Article).where(Article.id == article_id)
            .options(
                selectinload(Article.author),
                selectinload(Article.category),
                selectinload(Article.tags)
            )
        )
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none()
        
    async def update_article(self,user:User,article_id:int,data:ArticleUpdate):
        article = await self.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章ID不存在"
            )
        if data.title:
            article.title = data.title
        if data.content:
            article.content = data.content
        if data.summary:
            article.summary = data.summary
        if data.category_id:
            article.category_id = data.category_id
        if data.is_private:
            article.is_private = data.is_private

        article.author_id = user.id

        await self.db.commit()

        query = (
            select(Article).where(Article.id == article_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def delete_article(self,article_id:int):  
        article = await self.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章ID不存在"
            )
        await self.db.delete(article)
        return True
    
    async def publish_article(self,article_id:int):
        article = await self.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章ID不存在"
            )
        article.status = ArticleStatus.PUBLISHED
        article.published_at = func.now()
        await self.db.flush()
        await self.db.refresh(article)
        return article
    
    # 后续可做优化  redis 异步任务入库
    async def like_article(self,user:User,article_id:int):
        article = await self.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章ID不存在"
            )
        
        like_result = await self.db.execute(
            select(Like).where(Like.article_id == article_id,Like.user_id == user.id)
        )
        like = like_result.scalar_one_or_none()
        liked = True
        if like:
            stmt = (
                update(Article)
                .where(Article.id == article_id,Article.like_count > 0)
                .values(like_count=Article.like_count - 1)  # ✅ 关键：使用字段本身的值加1
                .returning(Article.like_count)  # 返回更新后的值
            )
            await self.db.delete(like)
            liked = False
        else:
            stmt = (
                update(Article)
                .where(Article.id == article_id)
                .values(like_count=Article.like_count + 1)  # ✅ 关键：使用字段本身的值加1
                .returning(Article.like_count)  # 返回更新后的值
            )
            # 同步like表
            like = Like(user_id=user.id,article_id=article_id)
            self.db.add(like)

        result = await self.db.execute(stmt)
        # 高并发的操作 需要commit
        await self.db.commit()

        count = result.scalar_one_or_none() or 0
        return liked,count