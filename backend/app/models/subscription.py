from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func,Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import CreateTimeBase,Base

class Subscription(CreateTimeBase,Base):
    __tablename__ = "subscriptions"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email : Mapped[str] = mapped_column(String(100), nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=False)
