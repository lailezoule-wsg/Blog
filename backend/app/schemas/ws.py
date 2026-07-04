import asyncio
import json
import logging
from typing import TypeVar,Generic

from pydantic import BaseModel,ConfigDict

logger = logging.getLogger(__name__)

T = TypeVar("T")

class WSBaseMessage(BaseModel,Generic[T]):
    type:str
    data:T|None

# 连接成功确认 `connected`
class WSConnectMessage(BaseModel):
    message:str = "WebSocket 连接成功"
    user_id:int
    connected_at:str
    

    model_config=ConfigDict(from_attributes=True)

# 文章发布通知 `article_published`
class WSArticlePubMessage(BaseModel):
    article_id:int
    title:str
    author:str
    published_at:str

# 新评论通知 `new_comment`
class WSCommentPubMessage(BaseModel):
    article_id:int
    comment_id:int
    commenter:str
    content:str
    created_at:str