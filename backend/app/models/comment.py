from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import CreateTimeBase,Base

if TYPE_CHECKING:
    from app.models.user import User

class Comment(CreateTimeBase,Base):
    __tablename__ = "comments"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content : Mapped[str] = mapped_column(Text, nullable=False)
    article_id : Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), nullable=False)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id : Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)
    is_approved : Mapped[bool] = mapped_column(Boolean, default=False)

    user : Mapped["User"] = relationship(
        "User",
        back_populates="comments",
        lazy="selectin"
    )
