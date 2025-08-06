import asyncio
from typing import NoReturn

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.timer import Timer, TimerPage
from backend.websocket_manager import WebsocketManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

edit_links: dict[str, TimerPage] = {}
public_links: dict[str, TimerPage] = {}
websocket_manager = WebsocketManager()


class NewTimer(BaseModel):
    """Model for creating a new timer."""

    duration: float


class ModifyPageSettings(BaseModel):
    """Model for modifying page settings."""

    name: str
    color: str


@app.post("/page/new")
async def new_page() -> dict:
    """Create a new page."""
    page = TimerPage(websocket_manager)
    edit_links[page.edit_link] = page
    public_links[page.public_link] = page

    return {"edit_link": page.edit_link}


@app.get("/page/{link}")
async def get_page(link: str) -> dict:
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
    await page.broadcast_update()


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
            await asyncio.sleep(10)
            await websocket.send_json(page.to_json())
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, page.public_link)
    except Exception as e:
        websocket_manager.disconnect(websocket, page.public_link)
        raise e from None
