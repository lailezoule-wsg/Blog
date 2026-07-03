from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import CreateTimeBase,Base

if TYPE_CHECKING:
    from app.models.article import Article

class Category(CreateTimeBase,Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer,nullable=False)
    description : Mapped[str] = mapped_column(Text, nullable=True)

    articles: Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="category",
        lazy="selectin"
    )