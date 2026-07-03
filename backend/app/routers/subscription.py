from typing import Annotated,Optional
from fastapi import APIRouter,Depends,HTTPException,status,Path

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import ResponseModel
from app.schemas.subscription import (
    SubscriptionResponse,SubscriptionCreate
)
from app.schemas.common import ResponseModel,PaginageResponse,PaginateData

from app.utils.depends import PaginateParams
from app.utils.depends import get_db,get_current_user,get_current_admin

from app.models.user import User

from app.services.subscription import SubscriptionService


DBSession = Annotated[AsyncSession,Depends(get_db)]

router = APIRouter(prefix="/api/subscribtions",tags=["订阅"])

@router.get("/",response_model=PaginageResponse[SubscriptionResponse])
async def list_sub(
    paginateParams:Annotated[PaginateParams,Depends()],
    current_admin:Annotated[User,Depends(get_current_admin)],
    db:DBSession
):
    service = SubscriptionService(db)
    total,subs = await service.list_sub(paginateParams)
    items = [SubscriptionResponse.model_validate(sub) for sub in subs]
    paginateData = PaginateData(
        page=paginateParams.page,
        size=paginateParams.size,
        total=total,
        items=items
    )
    return ResponseModel(data=paginateData)

@router.post("/",response_model=ResponseModel[SubscriptionResponse])
async def create_sub(
    data:SubscriptionCreate,
    db:DBSession
):
    service = SubscriptionService(db)
    sub = await service.create_sub(data)
    return ResponseModel(data=SubscriptionResponse.model_validate(sub))


@router.delete("/{email}",response_model=ResponseModel)
async def delete_sub(
    email:Annotated[str,Path(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')],
    db:DBSession
):
    service = SubscriptionService(db)
    await service.delete_sub(email)
    return ResponseModel(data="删除成功")