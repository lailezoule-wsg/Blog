from typing import Annotated,Optional
from fastapi import APIRouter,Depends,HTTPException,status,Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import ResponseModel
from app.schemas.article import (
    ArticleResponse,ArticleCreate,ArticleQuery,ArticleUpdate,ArticleSingleResponse,
    ArticlePublishResponse,ArticleLikeResponse,ArticleTagAdd
)
from app.schemas.common import ResponseModel,PaginageResponse,PaginateData
from app.schemas.tag import TagResponse
from app.schemas.comment import CommentCreate,CommentResponse,CommentCreateResponse

from app.utils.depends import PaginateParams
from app.utils.depends import get_db,get_current_user,get_current_user_optional

from app.models.user import User

from app.services.article import ArticleService
from app.services.ws import WSService


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
    await service.delete_article(current_user,article_id)
    return ResponseModel(data="删除成功")

@router.post("/{article_id}/publish",response_model=ResponseModel[ArticlePublishResponse])
async def publish_article(
    article_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    publish = await service.publish_article(current_user,article_id)
    # websocket通知
    wsService = WSService()
    await wsService.notify_new_article(article_id,publish.title,publish.author.username)
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

@router.post("/{article_id}/tags",response_model=ResponseModel)
async def add_tags(
    article_id:Annotated[int,Path(...,gt=0)],
    data:ArticleTagAdd,
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    tags = await service.add_tags(article_id,data)
    items = [TagResponse.model_validate(tag) for tag in tags]
    return ResponseModel(data={"tags":items})

@router.post("/{article_id}/tags/{tag_id}",response_model=ResponseModel)
async def delete_tags(
    article_id:Annotated[int,Path(...,gt=0)],
    tag_id:Annotated[int,Path(...,gt=0)],
    current_user:CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    await service.delete_tags(article_id,tag_id)
    return ResponseModel(data="标签已移除")

@router.get("/{article_id}/comments",response_model=PaginageResponse[CommentResponse])
async def list_comments(
    article_id:Annotated[int,Path(...,gt=0)],
    paginateParams:Annotated[PaginateParams,Depends()],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    db:DBSession
):
    service = ArticleService(db)
    total,comments = await service.list_comments(current_user,article_id,paginateParams)
    items = [CommentResponse.model_validate(comment) for comment in comments]
    paginateData = PaginateData(
        page=paginateParams.page,
        size=paginateParams.size,
        total=total,
        items=items
    )
    return ResponseModel(data=paginateData)

@router.post("/{article_id}/comments",response_model=ResponseModel[CommentCreateResponse])
async def add_comments(
    article_id:Annotated[int,Path(...,gt=0)],
    data:CommentCreate,
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    db:DBSession
):
    service = ArticleService(db)
    if current_user is None and data.nickname is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,"用户未登录或者匿名名称为空")
    author_id,comment = await service.add_comments(current_user,article_id,data)
    # websocket通知
    wsService = WSService()
    if current_user:
        commenter = current_user.username
    else:
        commenter = data.nickname if data.nickname else ""
    await wsService.notify_new_comment(article_id,comment.id,commenter,data.content,author_id)

    return ResponseModel(data=CommentResponse.model_validate(comment))

@router.put("/{article_id}/comments/{comment_id}",response_model=ResponseModel[CommentCreateResponse])
async def update_comments(
    article_id:Annotated[int,Path(...,gt=0)],
    comment_id:Annotated[int,Path(...,gt=0)],
    data:CommentCreate,
    current_user: CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    comments = await service.update_comments(current_user,article_id,comment_id,data)
    return ResponseModel(data=CommentResponse.model_validate(comments))

@router.delete("/{article_id}/comments/{comment_id}",response_model=ResponseModel)
async def delete_comments(
    article_id:Annotated[int,Path(...,gt=0)],
    comment_id:Annotated[int,Path(...,gt=0)],
    current_user: CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    await service.delete_comments(current_user,article_id,comment_id)
    return ResponseModel(data="删除成功")

@router.post("/{article_id}/comments/{comment_id}/approve",response_model=ResponseModel)
async def approve_comments(
    article_id:Annotated[int,Path(...,gt=0)],
    comment_id:Annotated[int,Path(...,gt=0)],
    current_user: CurrentUser,
    db:DBSession
):
    service = ArticleService(db)
    approve = await service.approve_comments(current_user,article_id,comment_id)
    return ResponseModel(data=approve)