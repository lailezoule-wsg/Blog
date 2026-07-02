from datetime import date,datetime
from typing import Annotated,Optional
from pydantic import BaseModel,Field,ConfigDict


class CategoryCreate(BaseModel):
    name:str = Field(...,max_length=50,description="分类名称，最长 50 字符")
    description:str | None = Field(None,max_length=200,description="分类描述，最长 200 字符")
    sort_order:int = Field(default=0,description="排序权重，默认 0")


class CategoryResponse(BaseModel):
    id:int
    name:str = Field(...,max_length=50,description="分类名称，最长 50 字符")
    description:str | None = Field(None,max_length=200,description="分类描述，最长 200 字符")
    sort_order:int | None = Field(None,description="排序权重，默认 0")
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)