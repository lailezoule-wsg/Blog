from fastapi import HTTPException,status,Depends
from sqlalchemy import select,update,delete,or_,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.article import ArticleCreate,ArticleQuery,ArticleUpdate,ArticleTagAdd
from app.schemas.comment import CommentCreate

from app.utils.depends import PaginateParams
from app.utils.enum import CommonOrderBy,ArticleStatus

from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag,article_tags
from app.models.like import Like
from app.models.comment import Comment

from app.services.tag import TagService
from app.services.category import CategoryService

class ArticleService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.tagService = TagService(db)
        self.categoryService = CategoryService(db)

    async def get_by_id(self,article_id:int,tag_flag:bool=False):
        query = select(Article).where(Article.id == article_id)
        if tag_flag:
            query = query.options(
                selectinload(Article.tags)
            )
        result = await self.db.execute(
            query
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章ID不存在"
            )
        return item
    
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
            tags = await self.tagService.get_by_ids(set(data.tag_ids))
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
        await self.get_by_id(article_id)
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
        await self.db.delete(article)
        return True
    
    async def publish_article(self,article_id:int):
        article = await self.get_by_id(article_id)
        article.status = ArticleStatus.PUBLISHED
        article.published_at = func.now()
        await self.db.flush()
        await self.db.refresh(article)
        return article
    
    # 后续可做优化  redis 异步任务入库
    async def like_article(self,user:User,article_id:int):
        await self.get_by_id(article_id)
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
    
    async def add_tags(self,article_id:int,data:ArticleTagAdd):
        article = await self.get_by_id(article_id,tag_flag=True)
        to_add = set()
        to_remove = set()
        stored_tag_ids = set()
        if article.tags:
            stored_tag_ids = {int(tag.id) for tag in article.tags}
        to_add = data.tag_ids - stored_tag_ids
        to_remove = stored_tag_ids - data.tag_ids
        
        if to_add:
            tags_list = await self.tagService.get_by_ids(to_add)
            article.tags.extend(tags_list)

        if to_remove:
            # 直接操作中间表删除（更高效）
            stmt = delete(article_tags).where(
                article_tags.c.article_id == article_id,
                article_tags.c.tag_id.in_(to_remove)
            )
            await self.db.execute(stmt)

        # 5. 提交事务
        await self.db.commit()
        await self.db.refresh(article)
        return article.tags
    
    async def add_comments(self,user:User|None,article_id:int,data:CommentCreate):
        await self.get_by_id(article_id,tag_flag=True)
        comment = Comment(
            content=data.content,
            parent_id=data.parent_id,
            article_id=article_id
        )

        user_id = user.id if user is not None else 1
        if user_id:
            comment.user_id = user_id
        if data.nickname:
            comment.nickname = data.nickname
        
        self.db.add(comment)
        await self.db.commit()
        # ✅ 关键修复：只刷新评论对象本身
        await self.db.refresh(comment)
        return comment
    
    async def list_comments(self,article_id:int,paginateParams:PaginateParams):
        await self.get_by_id(article_id)
        size = paginateParams.size
        offset = paginateParams.offset

        query = select(Comment).where(Comment.article_id == article_id)
        total_query = select(func.count(Comment.id)).where(Comment.article_id == article_id)

        query = query.options(
            selectinload(Comment.replies)
        )

        comments_results = await self.db.execute(
            query.offset(offset).limit(size)
        )
        comments = comments_results.scalars().all()
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one_or_none() or 0

        return total,comments
    
    async def get_comment_by_id(self,article_id:int,comment_id:int,user_id:int=0):
        query = (
            select(Comment).where(
                Comment.id == comment_id,
                Comment.article_id == article_id
            )
        )
        if user_id:
            query = query.where(Comment.user_id == user_id)

        result = await self.db.execute(
            query
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "评论不存在"
            )
        return item

    async def update_comments(self,user:User,article_id:int,comment_id:int,data:CommentCreate):
        await self.get_by_id(article_id)
        comment = await self.get_comment_by_id(article_id,comment_id)
        if comment.user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权编辑他人评论"
            )
        comment.content = data.content
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete_comments(self,user:User,article_id:int,comment_id:int):
        await self.get_by_id(article_id)
        comment = await self.get_comment_by_id(article_id,comment_id)
        if comment.user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权删除他人评论"
            )
        await self.db.delete(comment)
        return True
    

    async def approve_comments(self,user:User,article_id:int,comment_id:int):
        comment = await self.get_comment_by_id(article_id,comment_id,user.id)
        if comment.user_id != user.id and user.role != "admin":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权审批他人评论"
            )
        comment.is_approved = True
        await self.db.flush()
        await self.db.refresh(comment)
        return {"id":comment.id,"content":comment.content,"is_approved":comment.is_approved}
