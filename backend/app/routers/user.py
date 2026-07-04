import uuid
import os
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter,Depends,HTTPException,status,Form,File,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import ResponseModel
from app.schemas.user import (
    UserRegister,UserResponse,UserLogin,TokenResponse,TokenRefreshRequest,
    UserUpdate
)
from app.utils.depends import get_db,get_current_user,decode_token
from app.services.user import UserService

from app.utils.common import create_access_token,create_refresh_token
from app.config import settings
from app.services.file_service import FileUploadService

from app.models.user import User

router = APIRouter(prefix="/api/users",tags=["用户"])

DBSession = Annotated[AsyncSession,Depends(get_db)]
CurrentUser = Annotated[User,Depends(get_current_user)]

@router.post("/register",response_model=ResponseModel[UserResponse])
async def register(
    data:UserRegister,
    db:DBSession
):
    service = UserService(db)
    user = await service.register(data)
    return ResponseModel(data=UserResponse.model_validate(user))

# swagger 使用
@router.post("/login2",response_model=TokenResponse)
async def login2(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db:DBSession,
):
    service = UserService(db)
    data = UserLogin(username=username,password=password)
    tokens = await service.login(data)
    return tokens

@router.post("/login",response_model=ResponseModel[TokenResponse])
async def login(
    data:UserLogin,
    db:DBSession,
):
    service = UserService(db)
    tokens = await service.login(data)
    return ResponseModel(data=TokenResponse.model_validate(tokens))

@router.post("/refresh",response_model=ResponseModel[TokenResponse])
async def refresh(
    data:TokenRefreshRequest,
    current_user:CurrentUser,
):
    try:
        payload = decode_token(data.access_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 refresh token"
            )
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的 refresh token"
        )
    tokens = TokenResponse(
        access_token=create_access_token(current_user.id),
        refresh_token=create_refresh_token(current_user.id),
    )
    return ResponseModel(data=tokens)

@router.get("/me",response_model=ResponseModel[UserResponse])
async def me(
    current_user:CurrentUser,
    db:DBSession
):
    service = UserService(db)
    user = await service.me(current_user)
    return ResponseModel(data=UserResponse.model_validate(user))

@router.put("/me",response_model=ResponseModel[UserResponse])
async def update_me(
    data:UserUpdate,
    current_user:CurrentUser,
    db:DBSession
):
    service = UserService(db)
    user = await service.update_me(current_user,data)
    return ResponseModel(data=UserResponse.model_validate(user))

@router.post("/me/avatar",response_model=ResponseModel)
async def avatar(
    current_user:CurrentUser,
    db:DBSession,
    file:UploadFile = File(...),
    service: FileUploadService = Depends(FileUploadService)
):

    try:
        old_avatar = (current_user.avatar_url).split("/")[-1]
        # ✅ 验证文件
        await service.validate_file(
            file,
            max_size=settings.avatar_max_file_size,
            allowed_extensions=settings.avatar_allowed_extensions
        )
        
        # ✅ 保存文件（如果失败会自动抛出异常）
        filename = file.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        file_info = await service.save_file(
            file,
            subdir=settings.avatar_name,
            filename=filename  # 自动生成文件名
        )

        # 先删除原有头像
        await service.delete_file(settings.avatar_name,old_avatar)
        
        # 更新头像
        current_user.avatar_url = file_info["url"]
        await db.flush()
        await db.refresh(current_user)
        response = {
            "avatar_url":file_info["url"]
        }
        return ResponseModel(data=response)
    except HTTPException as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            e
        )