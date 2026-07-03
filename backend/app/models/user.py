from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column,relationship

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.like import Like
    from app.models.article import Article

class Base(DeclarativeBase):
    pass

class CreateTimeBase:
    __abstract__ = True  # 关键：标记为抽象类
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

class DateTimeBase:
    __abstract__ = True  # 关键：标记为抽象类
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

class User(DateTimeBase,Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username : Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email : Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password : Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url : Mapped[str] = mapped_column(String(255), nullable=True)
    role : Mapped[str] = mapped_column(String(50), default="user")
    bio : Mapped[str] = mapped_column(Text, nullable=True)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
    
    comments : Mapped[list["Comment"]] = relationship(
        "Comment", 
        back_populates="user",
        lazy="selectin",
    )

    likes : Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="user",
        lazy="selectin",
    )

    articles : Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="author",
        lazy="selectin",
    )



    