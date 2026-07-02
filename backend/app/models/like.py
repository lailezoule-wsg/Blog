from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import CreateTimeBase,Base
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.article import Article

class Like(CreateTimeBase,Base):
    __tablename__ = "likes"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    article_id : Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="likes",
        lazy="selectin"
    )

    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="likes",
        lazy="selectin"
    )
