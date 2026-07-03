from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status,Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.depends import get_db,get_current_user,decode_token

from app.schemas.common import ResponseModel
from app.schemas.article import (
    ArticleResponse,ArticleCreate,ArticleQuery,ArticleUpdate,ArticleSingleResponse,
    ArticlePublishResponse,ArticleLikeResponse
)
from app.schemas.common import ResponseModel,PaginageResponse,PaginateData
from app.utils.depends import PaginateParams


from app.models.user import User

from app.services.article import ArticleService

router = APIRouter(prefix="/api/articles",tags=["文章"])

DBSession = Annotated[AsyncSession,Depends(get_db)]
CurrentUser = Annotated[User,Depends(get_current_user)]

"""
默认行为（无 Depends）：当一个参数是 BaseModel 子类且没有 Depends 时，
FastAPI 会默认它来自请求体（Request Body）。
这就是为什么 POST/PUT 接口可以直接用 article: ArticleCreate。

使用 Depends()（或 Query）：当你在 GET 请求中，希望从 URL 的 ?key=value 部分获取参数时，
必须显式告诉 FastAPI。
"""
@router.get("/",response_model=PaginageResponse[ArticleResponse])
async def list_articles(
    paginateParams:Annotated[PaginateParams,Depends()],
    data:Annotated[ArticleQuery,Depends()],
    db:DBSession
):
    service = ArticleService(db)
    total,articles = await service.get_list(paginateParams,data)
    items = [ArticleResponse.model_validate(article) for article in articles]

    paginateData = PaginateData(
        page=paginateParams.page,
        size=paginateParams.size,
        total=total,
        items=items
    )
    return PaginageResponse(data=paginateData)

@router.get("/{article_id}",response_model=ResponseModel[ArticleResponse])
async def detail(
    article_id:Annotated[int,Path(...,gt=0)],
    db:DBSession
):
    service = ArticleService(db)
    article = await service.detail(article_id)
    return ResponseModel(data=ArticleResponse.model_validate(article))

@router.post("/",response_model=ResponseModel[ArticleResponse])
async def create(
    data:ArticleCreate,
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    article = await service.create(current_user,data)
    return ResponseModel(data=ArticleResponse.model_validate(article))

@router.put("/{article_id}",response_model=ResponseModel[ArticleSingleResponse])
async def update_article(
    article_id:Annotated[int,Path(...,gt=0)],
    data:ArticleUpdate,
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    article = await service.update_article(current_user,article_id,data)
    return ResponseModel(data=ArticleSingleResponse.model_validate(article))

@router.delete("/{article_id}",response_model=ResponseModel)
async def delete_article(
    article_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    await service.delete_article(article_id)
    return ResponseModel(data="删除成功")

@router.post("/{article_id}/publish",response_model=ResponseModel[ArticlePublishResponse])
async def publish_article(
    article_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    publish = await service.publish_article(article_id)
    return ResponseModel(data=ArticlePublishResponse.model_validate(publish))

@router.post("/{article_id}/like",response_model=ResponseModel[ArticleLikeResponse])
async def like_article(
    article_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    liked,like_count = await service.like_article(current_user,article_id)

    message = "点赞成功" if liked else "取消成功"
    return ResponseModel(
        message=message,
        data=ArticleLikeResponse(like_count=like_count,liked=liked)
    )