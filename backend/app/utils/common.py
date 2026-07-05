from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt
from fastapi import WebSocket
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# 加密
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# 验证密码
def verify_password(input_password: str, stored_password: str) -> bool:
    """Verify a password against a hashed password."""
    return bcrypt.checkpw(input_password.encode("utf-8"), stored_password.encode("utf-8"))

# 生成JWT
def create_access_token(user_id: int) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 生成刷新JWT
def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 解析JWT
def decode_token(token: str) -> dict:
    """Verify a JWT access token and return the payload."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

# ws token
def _extract_token(websocket: WebSocket) -> str | None:
    # 确保从 query_params 中提取
    if hasattr(websocket, "query_params"):
        return websocket.query_params.get("token")
    
    # 备用：从 scope 中解析
    query_string = websocket.scope.get("query_string", b"").decode()
    if query_string:
        params = dict(q.split("=") for q in query_string.split("&") if "=" in q)
        return params.get("token")
    return None

# ws token auth


def _authenticate(token: str) -> int | None:
    try:
        logger.debug(f"Decoding token: {token[:20]}...")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Token payload: {payload}")
        
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' field")
            return None
        
        # 检查 token 类型（如果是 access token）
        if payload.get("type") != "access":
            logger.warning(f"Invalid token type: {payload.get('type')}")
            return None
        
        return int(user_id)
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return None
    

