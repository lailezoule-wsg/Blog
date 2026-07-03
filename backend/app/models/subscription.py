from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import CreateTimeBase,Base

class Subscription(CreateTimeBase,Base):
    __tablename__ = "subscriptions"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email : Mapped[str] = mapped_column(String(100), unique=True,nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
