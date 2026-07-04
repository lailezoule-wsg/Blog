from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text,Enum,CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import DateTimeBase,Base
from app.utils.enum import ArticleStatus

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.like import Like
    from app.models.category import Category
    from app.models.user import User
    from app.models.comment import Comment


class Article(DateTimeBase,Base):
    __tablename__ = "articles"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title : Mapped[str] = mapped_column(String(200), nullable=False)
    content : Mapped[str] = mapped_column(Text, nullable=False)
    summary : Mapped[str] = mapped_column(String(500), nullable=False)
    cover_image : Mapped[str] = mapped_column(String(255), nullable=True)
    view_count : Mapped[int] = mapped_column(Integer, default=0)
    like_count : Mapped[int] = mapped_column(Integer, default=0)
    status : Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), 
        default=ArticleStatus.DRAFT,
        server_default=ArticleStatus.DRAFT.value,
        nullable=False
    )
    is_private : Mapped[bool] = mapped_column(Boolean, default=False)
    author_id : Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    category_id : Mapped[int] = mapped_column(ForeignKey("categories.id",ondelete="CASCADE"), nullable=False)

    published_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    tags : Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="article_tags",
        back_populates="articles",
        lazy="selectin"
    )

    comments : Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="article",
        lazy="selectin"
    )

    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates = "article",
        lazy = "selectin"
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates = "articles",
        lazy = "selectin"
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates = "articles",
        lazy = "selectin"
    )

    # ✅ 表级约束：确保点赞数不为负
    __table_args__ = (
        CheckConstraint('like_count >= 0', name='ck_like_count_positive'),
        CheckConstraint('view_count >= 0', name='ck_view_count_positive'),
    )