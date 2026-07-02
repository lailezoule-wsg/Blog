from fastapi import HTTPException,status,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.article import ArticleRequest

from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag

from app.services.tag import TagService
from app.services.category import CategoryService

class ArticleService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.tagService = TagService(db)
        self.categoryService = CategoryService(db)

    async def create(self,user:User,data:ArticleRequest):
        category = await self.categoryService.get_by_id(data.category_id)
        if not category:
            raise ValueError(f"分类 ID {data.category_id} 不存在")
        
        # 2. 验证标签是否存在
        tags = []
        if data.tag_ids:
            tags = await self.tagService.get_by_ids(data.tag_ids)
            if len(tags) != len(data.tag_ids):
                raise ValueError("部分标签不存在")
        # article = Article(
        #     title=data.title,
        #     content=data.content,
        #     summary=data.summary,
        #     category_id=data.category_id,
        #     is_private=data.is_private,
        #     author_id=data.author_id
        # )

        print("tags:",tags)

          # 4. 关联标签
        # if tags:
        #     article.tags = tags  # ✅ 直接赋值关联对象列表

        # # 5. 保存
        # self.db.add(article)
        # await self.db.commit()
        # await self.db.refresh(article)
        
        # return article

