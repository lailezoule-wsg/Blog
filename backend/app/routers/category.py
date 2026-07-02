from typing import Annotated
from fastapi import APIRouter,Query
from fastapi import APIRouter,Depends,HTTPException,status,Form,File,UploadFile

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.depends import get_db,get_current_user,decode_token

from app.schemas.common import ResponseModel,PaginageResponse,PaginateData
from app.schemas.category import CategoryCreate,CategoryResponse

from app.models.user import User

from app.services.category import CategoryService

from app.utils.depends import PaginateParams

router = APIRouter(prefix="/api/categories",tags=["分类"])

DBSession = Annotated[AsyncSession,Depends(get_db)]
CurrentUser = Annotated[User,Depends(get_current_user)]

@router.get("/",response_model=PaginageResponse[CategoryResponse])
async def list_categories(
    paginateParams:Annotated[PaginateParams,Depends()],
    current_user:CurrentUser,
    db:DBSession
):
    service = CategoryService(db)
    total , categories = await service.get_list(paginateParams)

    items = [CategoryResponse.model_validate(category) for category in categories]
    paginateData = PaginateData(
        page=paginateParams.page,
        size=paginateParams.size,
        total=total,
        items=items
    )
    return PaginageResponse(data=paginateData)


@router.post("/",response_model=ResponseModel[CategoryResponse])
async def create(
    data:CategoryCreate,
    current_user:CurrentUser,
    db:DBSession
):
    service = CategoryService(db)
    category = await service.create(data)
    return ResponseModel(data=CategoryResponse.model_validate(category))