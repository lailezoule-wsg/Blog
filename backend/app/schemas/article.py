import json
from datetime import date,datetime
from typing import Annotated,Optional
from pydantic import BaseModel,Field,ConfigDict
from fastapi import Depends,Form
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

class ArticleTagAdd(BaseModel):
    tag_ids:list[int] = Field(default_factory=list)

class ArticleCreate(BaseModel):
    title: str = Field(..., max_length=200, description="文章标题")
    content: str = Field(..., description="文章内容（Markdown 格式）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover_image: Optional[str] = Field(None, description="封面图路径")
    category_id: int = Field(..., description="分类ID")
    tag_ids: list[int] = Field(default_factory=list, description="标签列表")
    is_private: bool = Field(default=False, description="是否私密")
    status:ArticleStatus = ArticleStatus.DRAFT

    @classmethod
    def as_form(
        cls,
        title: str = Form(..., description="文章标题"),
        content: str = Form(..., description="文章内容"),
        summary: Optional[str] = Form(None, description="文章摘要"),
        cover_image: Optional[str] = Form(None, description="封面图路径"),
        category_id: int = Form(..., description="分类ID"),
        tag_ids: str = Form("[]", description="标签ID列表 (JSON数组)"),
        is_private: bool = Form(False, description="是否私密"),
        status: str = Form(ArticleStatus.DRAFT.value, description="文章状态"),
    ) -> "ArticleCreate":
        """
        从 Form 表单数据创建 ArticleCreate 实例
        
        用于支持文件上传的 multipart/form-data 请求
        """
        # 1. 解析 tag_ids
        tag_ids_list = cls._parse_tag_ids(tag_ids)
        
        # 2. 解析 status
        try:
            status_enum = ArticleStatus(status)
        except ValueError:
            status_enum = ArticleStatus.DRAFT
        
        # 3. 创建实例
        return cls(
            title=title,
            content=content,
            summary=summary,
            cover_image=cover_image,
            category_id=category_id,
            tag_ids=tag_ids_list,
            is_private=is_private,
            status=status_enum,
        )

    @staticmethod
    def _parse_tag_ids(tag_ids: str) -> list[int]:
        """
        解析 tag_ids JSON 字符串
        
        Args:
            tag_ids: JSON 数组字符串，如 "[1,2,3]" 或 "[]"
        
        Returns:
            List[int]: 标签ID列表
        """
        if not tag_ids or tag_ids.strip() == "":
            return []
        
        try:
            parsed = json.loads(tag_ids)
            if not isinstance(parsed, list):
                return []
            # 确保所有元素都是整数
            return [int(item) for item in parsed if item is not None]
        except (json.JSONDecodeError, ValueError, TypeError):
            return []

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
    status:ArticleStatus | None = None
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