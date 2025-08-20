import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, NoReturn

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from websockets import ConnectionClosed

from backend.constants import EXPIRATION
from backend.timer import Timer, TimerPage
from backend.utils import PrunableDict
from backend.websocket_manager import WebsocketManager

edit_links: PrunableDict[str, TimerPage] = PrunableDict()
public_links: PrunableDict[str, TimerPage] = PrunableDict()
websocket_manager = WebsocketManager()

client = AsyncMongoClient(os.environ.get("MONGO_URI"))
collection = client[os.environ.get("MONGO_DATABASE")].pages


async def create_tld_index() -> None:
    """Create the mongodb index that gives our storage a TTL."""
    await collection.create_index("last_modified", expireAfterSeconds=EXPIRATION)


async def reload_data() -> None:
    """Reload data from the DB."""
    async for document in collection.find():
        timers = []

        page = TimerPage(
            websocket_manager,
            collection,
            timers=timers,
            public_link=document["public_link"],
            edit_link=document["edit_link"],
            name=document["name"],
            color=document["color"],
            last_modified=datetime.fromisoformat(document["last_modified"]),
        )

        for timer in document["timers"]:
            timers.append(
                Timer(
                    -1,  # doesn't matter as we override all the other attributes
                    page,
                    websocket_manager,
                    unpaused_time=timer["unpaused_time"],
                    remaining_duration=timer["remaining_duration"],
                    is_paused=timer["is_paused"],
                    full_duration=timer["full_duration"],
                    name=timer["name"],
                )
            )
        page.timers = timers

        edit_links[document["edit_link"]] = page
        public_links[document["public_link"]] = page


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    """Run code during the lifespan of our app."""
    await create_tld_index()
    await reload_data()
    await remove_expired_entries()  # Start the periodic task to prune expired entries
    yield


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class NewTimer(BaseModel):
    """Model for creating a new timer."""

    duration: float


class ModifyPageSettings(BaseModel):
    """Model for modifying page settings."""

    name: str
    color: str


@repeat_every(seconds=3600)  # 1 hour
async def remove_expired_entries() -> None:
    """Remove expired entries from the edit and public links."""
    edit_links.prune()
    public_links.prune()


@app.post("/page/new")
@limiter.limit("5/minute")
async def new_page(request: Request) -> dict:
    """Create a new page."""
    page = TimerPage(websocket_manager, collection)
    await page.save()

    edit_links[page.edit_link] = page
    public_links[page.public_link] = page

    return {"edit_link": page.edit_link}


@app.get("/page/{link}")
@limiter.limit("10/minute")
async def get_page(link: str, request: Request) -> dict:
    """Get a timer page by its link."""
    public_page = public_links.get(link)
    if public_page:
        return {"page": public_page.to_json(), "permissions": "public"}

    edit_page = edit_links.get(link)
    if edit_page:
        return {"page": edit_page.to_json(), "permissions": "edit"}

    raise HTTPException(status_code=404, detail="Page not found")


def find_timer(edit_link: str, number: int) -> Timer:
    """Find a timer by its edit link and number."""
    page = edit_links.get(edit_link)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    if number < 0 or number >= len(page.timers):
        raise HTTPException(status_code=404, detail="Timer not found")

    return page.timers[number]


@app.post("/timer/{edit_link}/{number}/start", status_code=204)
async def start_timer(edit_link: str, number: int) -> None:
    """Start a timer by its edit link and number."""
    await find_timer(edit_link, number).start()


@app.post("/timer/{edit_link}/{number}/pause", status_code=204)
async def pause_timer(edit_link: str, number: int) -> None:
    """Pause a timer by its edit link and number."""
    await find_timer(edit_link, number).pause()


@app.post("/timer/{edit_link}/{number}/reset", status_code=204)
async def reset_timer(edit_link: str, number: int) -> None:
    """Reset a timer by its edit link and number."""
    await find_timer(edit_link, number).reset()


@app.delete("/timer/{edit_link}/{number}", status_code=204)
async def delete_timer(edit_link: str, number: int) -> None:
    """Delete a timer by its edit link and number."""
    page = edit_links.get(edit_link)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    try:
        await page.delete_timer(number)
    except IndexError:
        raise HTTPException(status_code=404, detail="Timer not found")


@app.post("/timer/{edit_link}/{number}/add_time/{seconds}", status_code=204)
async def add_time(edit_link: str, number: int, seconds: int) -> None:
    """Add time to the first timer on the page."""
    await find_timer(edit_link, number).add_time(seconds)


@app.post("/timer/{edit_link}/{number}/rename", status_code=204)
async def rename_timer(edit_link: str, number: int, name: str) -> None:
    """Rename a timer by its edit link and number."""
    await find_timer(edit_link, number).rename(name)


@app.post("/page/{edit_link}/timers", status_code=201)
async def create_timer(edit_link: str, new_timer: NewTimer) -> None:
    """Create a new timer on the page."""
    page = edit_links.get(edit_link)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await page.create_timer(new_timer.duration)


@app.put("/page/{edit_link}/settings", status_code=204)
async def modify_page_settings(edit_link: str, settings: ModifyPageSettings) -> None:
    """Modify the settings of a timer page."""
    page = edit_links.get(edit_link)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    page.name = settings.name
    page.color = settings.color

    # Broadcast the updated settings to all connected websockets
    await page.save()


@app.websocket("/subscribe/{link}")
async def websocket_subscribe(*, websocket: WebSocket, link: str) -> NoReturn:
    """Subscribe to updates for a specific link."""
    # Try to resolve the public link
    public_page = public_links.get(link)
    if not public_page:
        edit_page = edit_links.get(link)
        if not edit_page:
            await websocket.close(code=1000)
            return
        page = edit_page
    else:
        page = public_page

    await websocket_manager.connect(websocket, page.public_link)

    try:
        while True:
            await websocket.send_json(page.to_json())
            await asyncio.sleep(10)
    except (WebSocketDisconnect, ConnectionClosed):
        websocket_manager.disconnect(websocket, page.public_link)
    except Exception as e:
        websocket_manager.disconnect(websocket, page.public_link)
        raise e from None
