import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine
from app.models import Base

from app.utils.exceptions import setup_exception_handlers

from app.routers import user,tag,subscription,category,article,ws



from app.utils.logging import setup_logging, get_logger

from app.middles.request import RequestMiddleware





@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    # 文件创建
    settings.ensure_all_dirs()
    # 配置日志（在应用启动时调用一次）
    setup_logging(
        level=logging.INFO,           # 日志级别
        log_dir=settings.LOG_DIR,             # 日志文件目录
        use_json=False,               # 开发环境用文本，生产环境用 JSON
        console=True,                 # 输出到控制台
        file=True,                    # 输出到文件
    )
    # 获取根 Logger 必须:app  否则异常
    logger = get_logger("app")
    logger.info("Application starting...")
    # 数据库创建
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Perform any shutdown tasks here
    # 关闭时的清理
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    VERSION=settings.VERSION,
    lifespan=lifespan
)
"""
中间件的执行顺序（后添加的先执行）
"""
# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, 
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# 注册全局异常处理函数
setup_exception_handlers(app)

app.include_router(user.router)
app.include_router(tag.router)
app.include_router(category.router)
app.include_router(article.router)
app.include_router(subscription.router)
app.include_router(ws.router)

# 添加http请求中间件
app.add_middleware(RequestMiddleware)

# ✅ 批量挂载
for path, directory, name in settings.get_mount_configs():
    app.mount(path, StaticFiles(directory=directory), name=name)

@app.get("/")
async def root():
    return {"message": "Welcome to My Blog!"}
