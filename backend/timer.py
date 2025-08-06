from __future__ import annotations

import time

from backend.utils import random_string
from backend.websocket_manager import WebsocketManager


class TimerPage:
    """Represents a page that contains multiple timers and manages their state."""

    def __init__(self, websocket_manager: WebsocketManager) -> None:
        self.timers: list[Timer] = []
        self.public_link = random_string(8)
        self.edit_link = random_string(8)
        self.websocket_manager = websocket_manager
        self.name = "Cloud-synchronized chronometers"
        self.color = "indigo"

    async def create_timer(self, duration: float) -> None:
        """Create a new timer with the specified duration."""
        timer = Timer(duration, self, self.websocket_manager)
        self.timers.append(timer)
        await self.broadcast_update()

    async def delete_timer(self, index: int) -> None:
        """Delete a timer at the specified index."""
        if index < 0 or index >= len(self.timers):
            raise IndexError("Timer index out of range")

        del self.timers[index]
        await self.broadcast_update()

    async def broadcast_update(self) -> None:
        """Broadcast the current state of the timer to all connected websockets."""
        data = self.to_json()
        await self.websocket_manager.broadcast_update(self.public_link, data)

    def to_json(self) -> dict:
        """Convert the timer page to a JSON serializable dictionary."""
        return {
            "timers": [timer.to_json() for timer in self.timers],
            "public_link": self.public_link,
            "name": self.name,
            "color": self.color,
        }


class Timer:
    """Represents a single timer with start, pause, reset, and rename functionalities."""

    def __init__(
        self, duration: float, page: TimerPage, websocket_manager: WebsocketManager
    ) -> None:
        self.unpaused_time = None
        self.remaining_duration = duration
        self.is_paused = True

        self.websocket_manager = websocket_manager
        self.page = page
        self.name = "Chronometer"
        self.full_duration = duration

    async def start(self) -> None:
        """Start the timer."""
        if self.is_paused:
            self.unpaused_time = time.time()
            self.is_paused = False
            await self.page.broadcast_update()

    async def pause(self) -> None:
        """Pause the timer."""
        if not self.is_paused:
            elapsed_time = time.time() - self.unpaused_time
            self.remaining_duration -= elapsed_time
            self.is_paused = True
            self.unpaused_time = None
            await self.page.broadcast_update()

    async def reset(self) -> None:
        """Reset the timer to its full duration."""
        self.remaining_duration = self.full_duration
        self.is_paused = True
        self.unpaused_time = None
        await self.page.broadcast_update()

    async def add_time(self, additional_time: float) -> None:
        """Add time to the timer."""
        self.full_duration += additional_time
        self.remaining_duration += additional_time
        await self.page.broadcast_update()

    async def rename(self, new_name: str) -> None:
        """Rename the timer."""
        self.name = new_name
        await self.page.broadcast_update()

    def to_json(self) -> dict:
        """Convert the timer to a JSON serializable dictionary."""
        return {
            "unpaused_time": self.unpaused_time,
            "remaining_duration": self.remaining_duration,
            "is_paused": self.is_paused,
            "name": self.name,
            "full_duration": self.full_duration,
        }
