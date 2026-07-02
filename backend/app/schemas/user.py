from datetime import date,datetime
from typing import Annotated,Optional
from pydantic import BaseModel,EmailStr,Field,ConfigDict


class UserRegister(BaseModel):
    username:str = Field(...,min_length=3,max_length=30,description="用户名，3-50 字符")
    email:EmailStr = Field(...,description="邮箱，需符合邮箱格式")
    password:str = Field(...,min_length=8,description="密码，不少于 8 位")

class UserLogin(BaseModel):
    username:str = Field(...,min_length=3,max_length=30,description="用户名，3-50 字符")
    password:str = Field(...,min_length=8,description="密码，不少于 8 位")

class UserResponse(BaseModel):
    id:int
    username:str
    email:EmailStr
    avatar_url:Optional[str] = None
    bio:Optional[str] = None
    is_active:bool = True
    role:str = "user"
    created_at:datetime
    updated_at:datetime

    # 支持orm对象
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username:str = Field(...,min_length=3,max_length=30,description="用户名，3-50 字符")
    email:EmailStr = Field(...,description="邮箱，需符合邮箱格式")
    password:str = Field(...,min_length=8,description="密码，不少于 8 位")
    bio:str = Field(...,max_length=500,description="个人简介，最长 500 字符")

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str = "bearer"

class TokenRefreshRequest(BaseModel):
    access_token:str


