from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, tasks, users


app = FastAPI(title="SprintDesk API", version="1.0.0", docs_url="/api/docs", redoc_url=None)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
web = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=web), name="static")


@app.get("/api/health", tags=["Сервис"])
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(web / "index.html")
