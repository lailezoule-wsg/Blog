from fastapi import HTTPException,status,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.article import ArticleRequest

from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag

class TagService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def get_by_id(self,id:int):
        results = await self.db.get(Tag,id)
        return results
    
    async def get_by_ids(self,ids:list[int]):
        results = await self.db.execute(
            select(Tag).where(Tag.id.in_(ids))
        )
        return results.scalars().all()