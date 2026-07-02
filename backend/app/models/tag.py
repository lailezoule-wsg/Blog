from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text,Table,Column
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import Base,CreateTimeBase

if TYPE_CHECKING:
    from backend.app.models.article import Article

# 中间表
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Tag(CreateTimeBase,Base):
    __tablename__ = "tags"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    articles : Mapped[list["Article"]] = relationship(
        "Article",
        secondary=article_tags,
        back_populates="tags",
        lazy="selectin"
    )