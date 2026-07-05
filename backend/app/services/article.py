from fastapi import HTTPException,status,UploadFile
from sqlalchemy import select,update,delete,or_,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload,joinedload

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
from app.services.file_service import FileUploadService

from app.config import settings

from app.utils.logging import get_logger

logger = get_logger(__name__)

class ArticleService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.tagService = TagService(db)
        self.categoryService = CategoryService(db)

    async def get_by_id(self,article_id:int,tag_flag:bool=False,author_flag:bool=False):
        query = select(Article).where(Article.id == article_id)
        if tag_flag:
            query = query.options(
                selectinload(Article.tags)
            )
        if author_flag:
            query = query.options(
                selectinload(Article.author)
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

    async def create(self,user:User,data:ArticleCreate,file:UploadFile,fileService:FileUploadService):
        category = await self.categoryService.get_by_id(data.category_id)
        if not category:
            raise ValueError(f"分类 ID {data.category_id} 不存在")
        
        # 2. 验证标签是否存在
        tags = []
        if data.tag_ids:
            tags = await self.tagService.get_by_ids(set(data.tag_ids))
            if len(tags) != len(data.tag_ids):
                raise ValueError("部分标签不存在")
        cover_image = ""
        try:
            file_info = await fileService.img_save(
                file=file,
                subdir=settings.ARTICLE_PIC_NAME
            )
            cover_image = file_info["url"]
        except HTTPException as e:
            logger.error(f"文章封面上传失败：{str(e)}")

        article = Article(
            title=data.title,
            content=data.content,
            summary=data.summary,
            category_id=data.category_id,
            is_private=data.is_private,
            author_id=user.id,
            status=data.status,  # 确保有默认值
        )
        if cover_image:
            article.cover_image = cover_image
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
        await self._increment_view_count(article_id)

        article = result.scalar_one_or_none()
        await self.db.refresh(article)
        return article
    
    async def _increment_view_count(self, article_id: int) -> None:
        """增加文章浏览量（使用 UPDATE 语句，避免并发问题）"""
        try:
            # ✅ 使用 UPDATE 语句直接在数据库层面递增
            await self.db.execute(
                update(Article)
                .where(Article.id == article_id)
                .values(view_count=Article.view_count + 1)
            )
            await self.db.flush()  # 立即刷新到数据库
        except Exception as e:
            # 浏览量更新失败不应影响主流程，记录日志即可
            logger.warning(f"Failed to increment view count for article {article_id}: {e}")
        
    async def update_article(self,user:User,article_id:int,data:ArticleUpdate,file:UploadFile,fileService:FileUploadService):
        article = await self.get_by_id(article_id)
        if article.author_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权更新他人文章"
            )

        cover_image = ""
        old_pic = (article.cover_image).split("/")[-1] if article.cover_image else None
        try:
            file_info = await fileService.img_save(
                file=file,
                old_pic=old_pic,
                del_flag=True,
                subdir=settings.ARTICLE_PIC_NAME
            )
            cover_image = file_info["url"]
        except HTTPException as e:
            logger.error(f"文章封面上传失败：{str(e)}")

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
        if cover_image:
            article.cover_image = cover_image

        article.author_id = user.id

        await self.db.commit()

        query = (
            select(Article).where(Article.id == article_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def delete_article(self,user:User,article_id:int):  
        article = await self.get_by_id(article_id)
        if article.author_id != user.id and user.role != "admin":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权删除他人文章"
            )
        await self.db.delete(article)
        return True
    
    async def publish_article(self,user:User,article_id:int):
        article = await self.get_by_id(article_id,author_flag=True)
        if article.author_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权发布他人文章"
            )
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
        tag_ids = set(data.tag_ids)
        if article.tags:
            stored_tag_ids = {int(tag.id) for tag in article.tags}
        to_add = tag_ids - stored_tag_ids
        to_remove = stored_tag_ids - tag_ids
        
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
    
    async def delete_tags(self,article_id:int,tag_id:int):
        article = await self.get_by_id(article_id,tag_flag=True)
        to_remove = set()
        to_remove.add(tag_id)
        stored_tag_ids = set()
        if article.tags is None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "当前文章无任何标签，无法移除！"
            )
        stored_tag_ids = {int(tag.id) for tag in article.tags}
        to_remove = to_remove - stored_tag_ids

        if to_remove is None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "当前标签不属于该文章，无需移除！"
            )
        # 直接操作中间表删除（更高效）
        stmt = delete(article_tags).where(
            article_tags.c.article_id == article_id,
            article_tags.c.tag_id.in_(to_remove)
        )
        await self.db.execute(stmt)

        # 5. 提交事务
        await self.db.commit()
        await self.db.refresh(article)
        return True
    
    async def add_comments(self,user:User|None,article_id:int,data:CommentCreate):
        article = await self.get_by_id(article_id,tag_flag=True)

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
        return article.author_id,comment
    
    async def list_comments(self,user:User | None,article_id:int,paginateParams:PaginateParams):
        article = await self.get_by_id(article_id)
        size = paginateParams.size
        offset = paginateParams.offset

        query = select(Comment).where(Comment.article_id == article_id)
        total_query = select(func.count(Comment.id)).where(Comment.article_id == article_id)

        if user:
            if article.author_id == user.id or user.role == "admin":
                query = query
            else:
                query = query.where(
                or_(
                    Comment.user_id == user.id,
                    Comment.is_approved == True
                )
            )
        else:
            query = query.where(Comment.is_approved == True)

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
            ).options(joinedload(Comment.article).load_only(Article.author_id))
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
        if comment.user_id != user.id and user.role != "admin":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权删除他人评论"
            )
        await self.db.delete(comment)
        return True
    

    async def approve_comments(self,user:User,article_id:int,comment_id:int):
        comment = await self.get_comment_by_id(article_id,comment_id)
        if comment.article.author_id != user.id and user.role != "admin":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "无权审批评论"
            )
        comment.is_approved = True
        await self.db.flush()
        await self.db.refresh(comment)
        return {"id":comment.id,"content":comment.content,"is_approved":comment.is_approved}
