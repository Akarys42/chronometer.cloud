from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)  # Remember to tailor the CORS policies to your use case!


@app.get("/")
async def root() -> list:
    """Placeholder root endpoint."""
    return [{"id": 1, "content": "Post 1"}, {"id": 2, "content": "Post 2"}]
