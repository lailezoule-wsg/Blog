from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import (
    UserRegister,UserLogin,TokenResponse,UserUpdate
)
from app.models.user import User
from app.utils.common import (
    hash_password,verify_password,create_access_token,create_refresh_token
)

class UserService:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def get_by_username(self,username:str):
        results = await self.db.execute(
            select(User).where(User.username == username)
        )
        return results.scalar_one_or_none()
    
    async def get_by_email(self,email:str):
        results = await self.db.execute(
            select(User).where(User.username == email)
        )
        return results.scalar_one_or_none()
    
    async def get_by_id(self,id:int):
        results = await self.db.execute(
            select(User).where(User.id == id)
        )
        return results.scalar_one_or_none()

    async def register(self,data:UserRegister):
        if await self.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名已存在"
            )
        if await self.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱已存在"
            )
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password)
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def login(self,data:UserLogin):
        user = await self.get_by_username(data.username)
        if user is None or not verify_password(data.password,user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用",
            )
        tokens = TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
        return tokens
    
    async def me(self,user:User):
        return await self.get_by_id(user.id)
    
    async def update_me(self,user:User,data:UserUpdate):
        user.bio = data.bio
        user.email = data.email
        user.hashed_password = hash_password(data.password)
        await self.db.flush()
        await self.db.refresh(user)
        return user
      