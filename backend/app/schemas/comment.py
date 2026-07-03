from datetime import date,datetime
from typing import Annotated,Optional
from pydantic import BaseModel,Field,ConfigDict


class CommentCreate(BaseModel):
    content:str
    nickname:str | None = None
    parent_id:int = 0

class LocalAuthor(BaseModel):
    id:int
    username:str

    model_config=ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    id:int
    content:str
    article_id:int
    parent_id:int | None = None
    user_id:int | None = None
    is_approved:bool = False
    created_at:datetime
    user:Optional[LocalAuthor] = None

    model_config=ConfigDict(from_attributes=True)

class CommentResponse(CommentBase):
    replies:list["CommentBase"] = Field(default_factory=list)
    model_config=ConfigDict(from_attributes=True)

class CommentCreateResponse(CommentBase):

    model_config=ConfigDict(from_attributes=True)


    