from fastapi import HTTPException,status
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.subscription import SubscriptionCreate

from app.models.subscription import Subscription
from app.utils.depends import PaginateParams


class SubscriptionService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def list_sub(self,paginateParams:PaginateParams):
        size = paginateParams.size
        offset = paginateParams.offset

        results = await self.db.execute(
            select(Subscription).offset(offset).limit(size)
        )
        items = results.scalars().all()
        total_results = await self.db.execute(
            select(func.count(Subscription.id))
        )
        total = total_results.scalar_one_or_none() or 0
        return total,items

    async def create_sub(self,data:SubscriptionCreate):
        item = await self.get_by_emil(data.email)
        if item:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "邮箱已存在"
            )
        sub = Subscription(email=data.email)
        self.db.add(sub)
        await self.db.flush()
        await self.db.refresh(sub)
        return sub
    
    async def get_by_emil(self,email:str):
        result = await self.db.execute(
            select(Subscription).where(Subscription.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self,sub_id):
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == sub_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_sub(self,email:str):
        item = await self.get_by_emil(email)
        if item is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "邮箱不存在"
            )
        await self.db.delete(item)
        return True