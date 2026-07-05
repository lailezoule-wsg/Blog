import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.utils.websocket import manager
from app.schemas.ws import (
    WSBaseMessage,
    WSCommentPubMessage,
    WSArticlePubMessage,
)

from app.utils.logging import get_logger

logger = get_logger(__name__)

class WSService:
        
    # ============ 通知发送函数 ============
    @staticmethod
    async def notify_new_comment(
        article_id: int,
        comment_id: int,
        commenter: str,
        content: str,
        author_id: int,
    ):
        """
        通知文章作者有新评论
        """
        try:
            ws_comment_msg = WSCommentPubMessage(
                article_id=article_id,
                comment_id=comment_id,
                commenter=commenter,
                content=content,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

            message = WSBaseMessage[WSCommentPubMessage](
                type="new_comment",
                data=ws_comment_msg,
            )

            success = await manager.send_to_user(author_id, message.model_dump())

            if not success:
                logger.warning(f"Failed to send new_comment notification to user_id={author_id}")

            return success

        except Exception as e:
            logger.error(f"Error sending new_comment notification: {e}", exc_info=True)
            return False
        
    @staticmethod    
    async def notify_new_article(
        article_id: int, 
        title: str, 
        author: str
    ) -> bool:
        """
        广播新文章通知给所有在线用户
        """
        try:
            ws_article_msg = WSArticlePubMessage(
                article_id=article_id,
                title=title,
                author=author,
                published_at=datetime.now(timezone.utc).isoformat(),
            )

            message = WSBaseMessage[WSArticlePubMessage](
                type="article_published",
                data=ws_article_msg,
            )

            # 广播给所有在线用户
            await manager.broadcast(message.model_dump())
            logger.info(f"Broadcast new_article notification: article_id={article_id}")
            return True

        except Exception as e:
            logger.error(f"Error broadcasting new_article notification: {e}", exc_info=True)
            return False
        