from contextlib import suppress

from fastapi import WebSocket, WebSocketException
from websockets.exceptions import ConnectionClosed


class WebsocketManager:
    """Manages websocket connections for timer pages."""

    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, public_link: str) -> None:
        """Add a new websocket connection."""
        self.connections.setdefault(public_link, []).append(websocket)
        await websocket.accept()

    def disconnect(self, websocket: WebSocket, public_link: str) -> None:
        """Remove a websocket connection."""
        if public_link in self.connections:
            with suppress(ValueError):
                self.connections[public_link].remove(websocket)
                if not self.connections[public_link]:
                    del self.connections[public_link]

    async def broadcast_update(self, public_link: str, data: dict) -> None:
        """Broadcast an update to all connected websockets for a specific public link."""
        if public_link in self.connections:
            for websocket in self.connections[public_link]:
                try:
                    await websocket.send_json(data)
                except (WebSocketException, ConnectionClosed):
                    # Handle disconnection gracefully
                    self.disconnect(websocket, public_link)
