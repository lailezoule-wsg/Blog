from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker

from app.config import settings

"""
三步走：
1：创建引擎
2：创建工厂
3：创建会话 (使用时)
"""
engine = create_async_engine(
    settings.DATABASE_URL, 
    pool_size=20,          # 连接池大小
    max_overflow=40,       # 最大溢出连接数
    pool_pre_ping=True,    # 连接前检查是否有效
    pool_recycle=3600,     # 连接回收时间（秒）
    echo=False             # 生产环境关闭 SQL 日志
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)