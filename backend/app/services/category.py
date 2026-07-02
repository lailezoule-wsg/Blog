from fastapi import HTTPException,status,Depends
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryCreate

from app.models.category import Category
from app.utils.depends import PaginateParams

class CategoryService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def get_by_id(self,id:int):
        results = await self.db.get(Category,id)
        return results
    
    async def get_by_name(self,name:str):
        results = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return results.scalar_one_or_none()
    
    async def create(self,data:CategoryCreate):
        if await self.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在"
            )
        category = Category(
            name=data.name,
            description=data.description,
            sort_order=data.sort_order
        )
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def get_list(self,paginateParams:PaginateParams):
        page = paginateParams.page
        size = paginateParams.size
        offset = paginateParams.offset
        query = select(Category)

        total_result = await self.db.execute(
            select(func.count(Category.id))
        )
        total = total_result.scalar() or 0

        query = query.offset(offset).limit(size)

        results = await self.db.execute(
            query
        )
        return total , results.scalars().all()