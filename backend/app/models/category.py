from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean,Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import CreateTimeBase,Base

class Category(CreateTimeBase,Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer,nullable=False)
    description : Mapped[str] = mapped_column(Text, nullable=True)