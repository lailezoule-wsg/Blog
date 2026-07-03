from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey,UniqueConstraint,Index
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

     # ✅ 生产环境关键：为高频查询创建联合索引
    __table_args__ = (
        # 唯一约束（同时作为索引）
        UniqueConstraint('user_id', 'article_id', name='uq_user_article_like'),
        # 额外索引：用于查询某篇文章的所有点赞用户
        Index('ix_likes_article_id', 'article_id'),
        # 额外索引：用于查询用户的所有点赞
        Index('ix_likes_user_id', 'user_id'),
        # 联合索引：加速点赞状态查询
        Index('ix_likes_user_article', 'user_id', 'article_id'),
    )
