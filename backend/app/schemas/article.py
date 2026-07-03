from datetime import date,datetime
from typing import Annotated,Optional
from pydantic import BaseModel,Field,ConfigDict
from fastapi import Depends
from app.utils.enum import ArticleStatus,ArticleQuerySortBy,CommonOrderBy


class LocalAuthor(BaseModel):
    id:int
    username:str
    model_config = ConfigDict(from_attributes=True)

class LocalCategory(BaseModel):
    id:int
    name:str
    model_config = ConfigDict(from_attributes=True)

class LocalTags(BaseModel):
    id:int
    name:str
    model_config = ConfigDict(from_attributes=True)

class ArticleCreate(BaseModel):
    title: str = Field(..., max_length=200, description="文章标题")
    content: str = Field(..., description="文章内容（Markdown 格式）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover_image: Optional[str] = Field(None, description="封面图路径")
    category_id: int = Field(..., description="分类ID")
    tag_ids: list[int] = Field(default_factory=list, description="标签列表")
    is_private: bool = Field(default=False, description="是否私密")
    status:ArticleStatus = ArticleStatus.DRAFT

class ArticleResponse(BaseModel):
    id: int = Field(..., description="文章ID")
    title: str = Field(..., max_length=200, description="文章标题")
    content: str = Field(..., description="文章内容（Markdown 格式）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover_image: Optional[str] = Field(None, description="封面图路径")
    category_id: int = Field(..., description="分类ID")
    status:ArticleStatus = ArticleStatus.DRAFT
    author_id: int = Field(..., description="作者ID")
    is_private: bool = Field(default=False, description="是否私密")
    view_count: int = Field(default=0, description="浏览次数")
    like_count: int = Field(default=0, description="点赞数")
    comment_count: int = Field(default=0, description="评论数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 作者
    author:Optional[LocalAuthor] = Field(default=None, description="作者时间")
    # 分类
    category: Optional[LocalCategory] = Field(default=None,description="分类详情")
    # 标签
    tags: list[LocalTags] = Field(default_factory=list, description="标签列表")
    
    model_config = ConfigDict(from_attributes=True)

class ArticleSingleResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None = None
    cover_image: str | None = None
    category_id: int = 0
    status:ArticleStatus = ArticleStatus.DRAFT
    author_id: int
    is_private: bool = False
    view_count: int = 0
    like_count: int = 0
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleQuery(BaseModel):
    sort_by:ArticleQuerySortBy = ArticleQuerySortBy.CREATED
    order:CommonOrderBy = CommonOrderBy.DESC
    status:ArticleStatus = ArticleStatus.DRAFT
    category_id:int | None = None
    tag_id:int | None = None
    author_id:int | None = None
    q:str | None = None

class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    is_private: bool | None = None

class ArticlePublishResponse(BaseModel):
    id: int
    title: str
    status:ArticleStatus = ArticleStatus.PUBLISHED
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArticleLikeResponse(BaseModel):
    liked:bool = False
    like_count: int
    
    model_config = ConfigDict(from_attributes=True)