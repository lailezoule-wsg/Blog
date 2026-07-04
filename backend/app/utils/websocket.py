# app/utils/websocket.py
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._connections: Dict[int, WebSocket] = {}  # user_id -> WebSocket
        self._lock = asyncio.Lock()

    async def register(self, websocket: WebSocket, user_id: int) -> None:
        """注册连接"""
        async with self._lock:
            # 如果用户已有连接，先关闭旧连接
            if user_id in self._connections:
                try:
                    await self._connections[user_id].close()
                except Exception:
                    pass
            self._connections[user_id] = websocket
            logger.info(f"User {user_id} registered")

    async def deregister(self, websocket: WebSocket) -> None:
        """注销连接"""
        async with self._lock:
            for user_id, ws in list(self._connections.items()):
                if ws == websocket:
                    del self._connections[user_id]
                    logger.info(f"User {user_id} deregistered")
                    break

    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> bool:
        """发送消息给指定用户"""
        websocket = self._connections.get(user_id)
        if not websocket:
            return False

        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Send to user {user_id} failed: {e}")
            return False

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[list[int]] = None) -> None:
        """广播消息给所有在线用户"""
        exclude = exclude or []
        tasks = []
        for user_id, websocket in self._connections.items():
            if user_id not in exclude:
                tasks.append(self.send_to_user(user_id, message))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for user_id, result in zip(self._connections.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Broadcast to user {user_id} failed: {result}")

    def get_online_users(self) -> list[int]:
        """获取所有在线用户ID"""
        return list(self._connections.keys())

    def is_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self._connections


# 全局单例
manager = ConnectionManager()