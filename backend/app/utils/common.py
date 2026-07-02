from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt

from app.config import settings

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 生成刷新JWT
def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 解析JWT
def decode_token(token: str) -> dict:
    """Verify a JWT access token and return the payload."""
    return jwt.decode(token, settings.secret_key, algorithms=settings.ALGORITHM)
    

