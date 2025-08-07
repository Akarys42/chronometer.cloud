from __future__ import annotations

import time
from datetime import datetime

from pymongo.asynchronous.collection import AsyncCollection

from backend.constants import EXPIRATION
from backend.utils import Expirable, random_string
from backend.websocket_manager import WebsocketManager


class TimerPage(Expirable):
    """Represents a page that contains multiple timers and manages their state."""

    def __init__(
        self,
        websocket_manager: WebsocketManager,
        db_collection: AsyncCollection,
        *,
        timers: list[Timer] = None,
        public_link: str = None,
        edit_link: str = None,
        name: str = "Cloud-synchronized chronometers",
        color: str = "indigo",
        last_modified: datetime = None,
    ) -> None:
        self.timers = timers or []
        self.public_link = public_link or random_string(8)
        self.edit_link = edit_link or random_string(8)

        self.name = name
        self.color = color
        self.last_modified = last_modified or datetime.now()

        self.websocket_manager = websocket_manager
        self.db_collection = db_collection

    async def create_timer(self, duration: float) -> None:
        """Create a new timer with the specified duration."""
        timer = Timer(duration, self, self.websocket_manager)
        self.timers.append(timer)
        await self.save()

    async def delete_timer(self, index: int) -> None:
        """Delete a timer at the specified index."""
        if index < 0 or index >= len(self.timers):
            raise IndexError("Timer index out of range")

        del self.timers[index]
        await self.save()

    async def save(self) -> None:
        """Commit the page to the DB and broadcast updates."""
        self.last_modified = datetime.now()
        data = self.to_json()
        await self.broadcast_update(data)
        data["_id"] = self.public_link
        data["edit_link"] = self.edit_link
        data["last_modified"] = self.last_modified.isoformat()

        await self.db_collection.replace_one({"_id": self.public_link}, data, upsert=True)

    async def broadcast_update(self, data: dict) -> None:
        """Broadcast the current state of the timer to all connected websockets."""
        await self.websocket_manager.broadcast_update(self.public_link, data)

    def to_json(self) -> dict:
        """Convert the timer page to a JSON serializable dictionary."""
        return {
            "timers": [timer.to_json() for timer in self.timers],
            "public_link": self.public_link,
            "name": self.name,
            "color": self.color,
        }

    def is_expired(self) -> bool:
        """Check if the page is expired based on its last modified time."""
        return (datetime.now() - self.last_modified).total_seconds() > EXPIRATION


class Timer:
    """Represents a single timer with start, pause, reset, and rename functionalities."""

    def __init__(
        self,
        duration: float,
        page: TimerPage,
        websocket_manager: WebsocketManager,
        *,
        unpaused_time: float | None = None,
        remaining_duration: float = None,
        is_paused: bool = True,
        full_duration: float = None,
        name: str = "Chronometer",
    ) -> None:
        self.unpaused_time = unpaused_time
        self.remaining_duration = remaining_duration or duration
        self.is_paused = is_paused
        self.full_duration = full_duration or duration
        self.name = name

        self.websocket_manager = websocket_manager
        self.page = page

    async def start(self) -> None:
        """Start the timer."""
        if self.is_paused:
            self.unpaused_time = time.time()
            self.is_paused = False
            await self.page.save()

    async def pause(self) -> None:
        """Pause the timer."""
        if not self.is_paused:
            elapsed_time = time.time() - self.unpaused_time
            self.remaining_duration -= elapsed_time
            self.is_paused = True
            self.unpaused_time = None
            await self.page.save()

    async def reset(self) -> None:
        """Reset the timer to its full duration."""
        self.remaining_duration = self.full_duration
        self.is_paused = True
        self.unpaused_time = None
        await self.page.save()

    async def add_time(self, additional_time: float) -> None:
        """Add time to the timer."""
        self.full_duration += additional_time
        self.remaining_duration += additional_time
        await self.page.save()

    async def rename(self, new_name: str) -> None:
        """Rename the timer."""
        self.name = new_name
        await self.page.save()

    def to_json(self) -> dict:
        """Convert the timer to a JSON serializable dictionary."""
        return {
            "unpaused_time": self.unpaused_time,
            "remaining_duration": self.remaining_duration,
            "is_paused": self.is_paused,
            "name": self.name,
            "full_duration": self.full_duration,
        }
