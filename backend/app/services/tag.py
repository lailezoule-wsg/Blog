from typing import Annotated
from fastapi import HTTPException,status,Depends
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import ResponseModel,PaginageResponse,PaginateData
from app.schemas.tag import TagCreate

from app.models.tag import Tag
from app.utils.depends import PaginateParams

class TagService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def get_by_id(self,id:int):
        results = await self.db.get(Tag,id)
        return results
    
    async def get_by_ids(self,ids:set[int]):
        results = await self.db.execute(
            select(Tag).where(Tag.id.in_(ids))
        )
        return results.scalars().all()
    
    async def get_by_name(self,name:str):
        results = await self.db.execute(
            select(Tag).where(Tag.name == name)
        )
        return results.scalar_one_or_none()
    
    async def list_tags(self,paginageParam:Annotated[PaginateParams,Depends()]):
        size = paginageParam.size
        offset = paginageParam.offset
        query = select(Tag)
        total_result = await self.db.execute(
            select(func.count(Tag.id))
        )
        total = total_result.scalar() or 0

        results =await self.db.execute(
            query.offset(offset).limit(size)
        )
        results = results.scalars().all()
        return total, results
    
    async def create_tag(self,data:TagCreate):
        if await self.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签已存在"
            )
        tag = Tag(name=data.name)
        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag
    
    async def check_by_id_name(self,tag_id:int,name:str):
        results = await self.db.execute(
            select(Tag).where(Tag.id != tag_id,Tag.name == name)
        )
        return results.scalar_one_or_none()
    
    async def update_tag(self,tag_id:int,data:TagCreate):
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签不存在"
            )
        checkIdName = await self.check_by_id_name(tag_id,data.name)
        if checkIdName:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )
        tag.name=data.name
        await self.db.flush()
        await self.db.refresh(tag)
        return tag
    
    async def delete_tag(self,tag_id:int):
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签不存在"
            )
        await self.db.delete(tag)
        return True
