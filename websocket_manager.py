from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """Менеджер WebSocket соединений для уведомлений"""

    def __init__(self):
        # Храним активные соединения: user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключить пользователя"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Отключить пользователя"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(
        self, message: dict, user_id: int
    ):
        """Отправить личное сообщение пользователю"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                # Если соединение закрыто, удаляем его
                self.disconnect(user_id)
                print(f"Error sending message to user {user_id}: {e}")

    async def send_notification(
        self, user_id: int, notification_type: str, message: str, data: dict = None
    ):
        """Отправить уведомление пользователю"""
        notification = {
            "type": notification_type,
            "message": message,
            "data": data or {}
        }
        await self.send_personal_message(notification, user_id)

    async def broadcast(self, message: dict):
        """Отправить сообщение всем подключенным пользователям"""
        disconnected = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                disconnected.append(user_id)
                print(f"Error broadcasting to user {user_id}: {e}")

        # Удаляем отключенные соединения
        for user_id in disconnected:
            self.disconnect(user_id)


# Глобальный менеджер соединений
manager = ConnectionManager()




