from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # app 设置
    APP_NAME: str = "My Blog"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A simple blog application built with FastAPI."
    DEBUG: bool = True

    # 数据库设置
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # JWT 设置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"

    # websocket 设置
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_HEARTBEAT_TIMEOUT: int = 10

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("./logs")
    LOG_USE_JSON: bool = False

    # Token 设置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # 上传路径
    UPLOAD_DIR: str = "uploads"

    # 头像限制
    AVATAR_ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif"}
    AVATAR_MAX_FILE_SIZE : int = 2 * 1024 * 1024  # 2MB
    AVATAR_NAME:str = "avatar"
    AVATAR_DIR: str = "uploads/avatar"

    # 跨域 credentials
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8000"]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]
    ALLOWED_CREDENTIALS: bool = True

    # 文章
    ARTICLE_PIC_DIR:str = "uploads/article_pic"
    ARTICLE_PIC_NAME:str = "article_pic"

    def ensure_all_dirs(self):
        """确保所有目录存在"""
        dirs = [
            self.UPLOAD_DIR,
            self.AVATAR_DIR,
            self.ARTICLE_PIC_DIR
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get_mount_configs(self):
        """获取挂载配置"""
        return [
            ("/uploads/avatar", self.AVATAR_DIR, "avatar"),
            ("/uploads/article_pic", self.ARTICLE_PIC_DIR, "article_pic")
        ]

    model_config = {
        "env_file" : ".env",
        "env_file_encoding" : "utf-8"
    }

settings = Settings()