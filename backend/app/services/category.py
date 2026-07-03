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
    
    async def check_by_id_name(self,category_id:int,name:str):
        results = await self.db.execute(
            select(Category).where(Category.id != category_id,Category.name == name)
        )
        return results.scalar_one_or_none()
    
    async def update_category(self,category_id:int,data:CategoryCreate):
        category = await self.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类ID不存在"
            )
        if data.name:
            checkIdName = await self.check_by_id_name(category_id,data.name)
            if checkIdName:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类名称已存在"
                )
            category.name = data.name
        if data.description:
            category.description = data.description
        if data.sort_order:
            category.sort_order = data.sort_order
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def delete_category(self,category_id:int):
        category = await self.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类ID不存在"
            )
        await self.db.delete(category)
        return True
