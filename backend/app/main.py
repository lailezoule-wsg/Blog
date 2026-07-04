import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine
from app.models import Base

from app.utils.exceptions import setup_exception_handlers

from app.routers import user,tag,subscription,category,article,ws

# 文件创建
settings.ensure_all_dirs()

from app.utils.logging import setup_logging, get_logger
import logging

# 配置日志（在应用启动时调用一次）
setup_logging(
    level=logging.INFO,           # 日志级别
    log_dir="./logs",             # 日志文件目录
    use_json=False,               # 开发环境用文本，生产环境用 JSON
    console=True,                 # 输出到控制台
    file=True,                    # 输出到文件
)

# 获取根 Logger
logger = get_logger("app")
logger.info("Application starting...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    # 数据库创建
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Perform any shutdown tasks here

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "http://localhost:5173", "http://localhost:8000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
@app.middleware("http")
async def http_process_time(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url} completed in {process_time:.4f} seconds")
    return response


relative_avatar_path = settings.avatar_dir
avatar_name = relative_avatar_path.split("/")[-1]

# ✅ 批量挂载
for path, directory, name in settings.get_mount_configs():
    app.mount(path, StaticFiles(directory=directory), name=name)

@app.get("/")
async def root():
    return {"message": "Welcome to My Blog!"}