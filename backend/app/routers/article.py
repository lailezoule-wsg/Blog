from typing import Annotated
from fastapi import APIRouter
from fastapi import APIRouter,Depends,HTTPException,status,Form,File,UploadFile

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.depends import get_db,get_current_user,decode_token

from app.schemas.common import ResponseModel
from app.schemas.article import ArticleResponse,ArticleRequest

from app.models.user import User

from app.services.article import ArticleService

router = APIRouter(prefix="/api/articles",tags=["文章"])

DBSession = Annotated[AsyncSession,Depends(get_db)]
CurrentUser = Annotated[User,Depends(get_current_user)]

@router.get("/")
async def list_articles():
    pass

@router.post("/",response_model=ResponseModel[ArticleResponse])
async def create(
    data:ArticleRequest,
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    article = await service.create(current_user,data)
    print("article:",article)