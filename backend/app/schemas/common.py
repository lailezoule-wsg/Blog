from typing import Annotated,TypeVar,Generic
from pydantic import BaseModel

# 任意类型
T = TypeVar("T")

# 通用的响应
class ResponseModel(BaseModel,Generic[T]):
    code:int=200
    message:str="success"
    data:T|None

# 通用的分页
class PaginateData(BaseModel,Generic[T]):
    page:int
    size:int
    total:int
    items:list[T]

# 通用的分页响应
class PaginageResponse(BaseModel,Generic[T]):
    code:int=200
    message:str="success"
    data:PaginateData[T]
