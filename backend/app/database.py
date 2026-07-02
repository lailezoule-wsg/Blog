from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker

from app.config import settings

"""
三步走：
1：创建引擎
2：创建工厂
3：创建会话 (使用时)
"""
engine = create_async_engine(
    settings.database_url, 
    echo=True, 
    future=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)