from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My Blog"
    version: str = "1.0.0"
    description: str = "A simple blog application built with FastAPI."
    debug: bool = True

    # Async Database settings
    database_url: str = "sqlite+aiosqlite:///./test.db"

    # JWT settings
    secret_key: str = "your-secret-key"
    ALGORITHM: str = "HS256"

    # Token expiration settings
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # 上传路径
    upload_dir: str = "uploads"

    # 头像限制
    avatar_allowed_extensions: set = {".jpg", ".jpeg", ".png", ".gif"}
    avatar_max_file_size : int = 2 * 1024 * 1024  # 2MB
    avatar_dir: str = "uploads/avatar"

    def ensure_all_dirs(self):
        """确保所有目录存在"""
        dirs = [
            self.upload_dir,
            self.avatar_dir,
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get_mount_configs(self):
        """获取挂载配置"""
        return [
            ("/uploads/avatar", self.avatar_dir, "avatar")
        ]

    model_config = {
        "env_file": ".env",
    }

settings = Settings()