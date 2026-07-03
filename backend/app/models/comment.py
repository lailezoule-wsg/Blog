from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Boolean,Text,CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.models.user import CreateTimeBase,Base

if TYPE_CHECKING:
    from app.models.user import User

class Comment(CreateTimeBase,Base):
    __tablename__ = "comments"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content : Mapped[str] = mapped_column(Text, nullable=False)
    article_id : Mapped[int] = mapped_column(Integer, ForeignKey("articles.id",ondelete="CASCADE"), nullable=False)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=True)
    parent_id : Mapped[int] = mapped_column(Integer, ForeignKey("comments.id",ondelete="CASCADE"), nullable=True)
    is_approved : Mapped[bool] = mapped_column(Boolean, default=False)
    nickname:Mapped[str] = mapped_column(String(100),nullable=True)

    user : Mapped["User"] = relationship(
        "User",
        back_populates="comments",
        lazy="selectin"
    )

    # ✅ 自关联：父级评论（这条评论的父评论）
    parent: Mapped["Comment | None"] = relationship(
        "Comment",
        remote_side=[id],  # ✅ 关键：指定 id 为远程侧
        back_populates="replies",
        lazy="selectin"
    )

    # ✅ 自关联：回复列表（这条评论的所有子评论）
    replies: Mapped[list["Comment | None"]] = relationship(
        "Comment",
        back_populates="parent",
        lazy="selectin"
    )

    # ✅ 优化6：添加表级约束
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL) OR (nickname IS NOT NULL)",
            name="ck_comment_user_or_nickname"
        ),
    )
