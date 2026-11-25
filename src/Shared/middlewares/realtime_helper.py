"""WebSocket ConnectionManager & Realtime Push Helper (Thái - M09)."""
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_clients: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_clients[str(user_id)] = websocket

    def disconnect(self, user_id: str) -> None:
        self.active_clients.pop(str(user_id), None)

    async def send_notification(self, user_id: str, event_type: str, payload: dict) -> bool:
        ws = self.active_clients.get(str(user_id))
        if ws is None:
            return False
        await ws.send_json({"event": event_type, "payload": payload})
        return True


manager = ConnectionManager()
