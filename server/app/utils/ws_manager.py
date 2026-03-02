from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # username -> websocket

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    def notify_user(self, username: str, message: dict):
        if username in self.active_connections:
            asyncio.create_task(
                self.active_connections[username].send_json(message)
            )

manager = ConnectionManager()