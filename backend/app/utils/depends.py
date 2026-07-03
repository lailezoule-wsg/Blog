from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends,HTTPException,Query,status
from fastapi.security import OAuth2PasswordBearer

from app.database import async_session
from app.utils.common import decode_token
from app.config import settings

from app.models.user import User

# OAuth2PasswordBearer是FastAPI提供的一个类，
# 用于处理基于OAuth2的密码模式认证。它会从请求中提取Authorization头部的Bearer token，
# 并将其作为字符串返回。tokenUrl参数指定了用于获取访问令牌的URL路径。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login2")

# 获取异步数据库会话
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# 获取用户信息
async def get_current_user(
  token:Annotated[str,Depends(oauth2_scheme)],
  db:Annotated[AsyncSession,Depends(get_db)]      
):
    print("token:",token)
    exception_alert = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 已过期或无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise exception_alert
        user_id = int(user_id)
    except Exception:
        raise exception_alert
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise exception_alert
    return user

# 获取admin信息
async def get_current_admin(
        current_user:Annotated[User,Depends(get_current_user)]
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user

# 分页参数封装
class PaginateParams:
    def __init__(
            self,
            page:Annotated[int,Query(ge=1)] = 1,
            size:Annotated[int,Query(ge=1,le=100)] = 20
        ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size
    

