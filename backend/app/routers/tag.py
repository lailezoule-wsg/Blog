from typing import Annotated
from fastapi import APIRouter,Query,Path
from fastapi import APIRouter,Depends,HTTPException,status

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.depends import get_db,get_current_user,get_current_admin

from app.schemas.common import ResponseModel,PaginageResponse,PaginateData
from app.schemas.tag import TagCreate,TagResponse

from app.models.user import User

from app.services.tag import TagService

from app.utils.depends import PaginateParams


DBSession = Annotated[AsyncSession,Depends(get_db)]
CurrentUser = Annotated[User,Depends(get_current_user)]
CurrentAdmin = Annotated[User,Depends(get_current_admin)]

router = APIRouter(prefix="/api/tags",tags=["标签"])

@router.get("/",response_model=PaginageResponse[TagResponse])
async def list_tags(
    paginageParam:Annotated[PaginateParams,Depends()],
    current_user:CurrentUser,
    db:DBSession
):
    service = TagService(db)
    total,tags = await service.list_tags(paginageParam)
    items = [TagResponse.model_validate(tag) for tag in tags]
    paginateData = PaginateData(
        page=paginageParam.page,
        size=paginageParam.size,
        total=total,
        items=items
    )
    return PaginageResponse(data=paginateData)

@router.post("/",response_model=ResponseModel[TagResponse])
async def create_tag(
    data:TagCreate,
    current_user:CurrentUser,
    db:DBSession
):
    service = TagService(db)
    tag = await service.create_tag(data)
    return ResponseModel(data=TagResponse.model_validate(tag))

@router.put("/{tag_id}",response_model=ResponseModel[TagResponse])
async def update_tag(
    tag_id:Annotated[int,Path(...,gt=0)],
    data:TagCreate,
    current_user:CurrentAdmin,
    db:DBSession
):
    service = TagService(db)
    tag = await service.update_tag(tag_id,data)
    return ResponseModel(data=TagResponse.model_validate(tag))

@router.delete("/{tag_id}",response_model=ResponseModel)
async def delete_tag(
    tag_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentAdmin,
    db:DBSession
):
    service = TagService(db)
    await service.delete_tag(tag_id)
    return ResponseModel(data="删除成功")


    