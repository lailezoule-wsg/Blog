import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.utils.websocket import manager
from app.utils.common import _authenticate, _extract_token
from app.schemas.ws import (
    WSBaseMessage,
    WSConnectMessage,
)

from app.services.ws import WSService

from app.utils.logging import get_logger

router = APIRouter(tags=["WebSocket"])

logger = get_logger(__name__)

# ============ WebSocket 端点 ============
@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket 通知端点"""

    # ========== 第一行日志 ==========
    logger.error("🚀 WebSocket endpoint REACHED!")  # 用 ERROR 级别确保能看到

    # ===== 1. 认证阶段 =====
    token = _extract_token(websocket)
    logger.info(f"WebSocket connection with token: {token[:20] if token else 'None'}...")
    
    if not token:
        logger.warning("Missing token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return
    
    user_id = _authenticate(token)
    if user_id is None:
        logger.warning(f"Invalid token: {token[:20]}...")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return
    
    # ===== 2. 接受连接 =====
    logger.info(f"✅ WebSocket accepted for user_id={user_id}")
    """
    await websocket.accept()
    # 作用：完成 WebSocket 握手（HTTP → WebSocket 协议升级）
    # 结果：websocket 对象进入"已连接"状态，可以收发消息
    # 保存了：连接状态、协议参数、底层网络连接
    """
    await websocket.accept()
    """
    await manager.register(websocket, user_id)
    # 作用：将 websocket 对象注册到连接管理器
    # 结果：websocket 被保存到管理器的字典中，供后续使用
    # 保存了：user_id → websocket 的映射关系
    """
    await manager.register(websocket, user_id)
    
    # ===== 3. 发送连接成功消息 =====
    try:
        connect_msg = WSConnectMessage(
            user_id=user_id,
            connected_at=datetime.now(timezone.utc).isoformat(),
        )
        await websocket.send_json(
            WSBaseMessage(
                type="connected",
                data=connect_msg.model_dump(),
            ).model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to send connected message: {e}")
    
    # ===== 4. 消息循环 =====
    try:
        while True:
            data = await websocket.receive()
            
            if data["type"] == "websocket.disconnect":
                logger.info(f"WebSocket disconnected: user_id={user_id}")
                break
            
            if data.get("type") == "websocket.receive" and "text" in data:
                try:
                    msg = json.loads(data["text"])
                    if msg.get("type") == "pong":
                        continue
                    # 处理其他消息...
                except json.JSONDecodeError:
                    pass
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        await manager.deregister(websocket)
        logger.info(f"WebSocket cleaned up: user_id={user_id}")


# ============ 通知发送函数 ============
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
    service = WSService()
    return await service.notify_new_comment(
        article_id,
        comment_id,
        commenter,
        content,
        author_id,
    )


async def notify_new_article(article_id: int, title: str, author: str) -> bool:
    """
    广播新文章通知给所有在线用户
    """
    service = WSService()
    return await service.notify_new_article(
        article_id,
        title,
        author,
    )
    