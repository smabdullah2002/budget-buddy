from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .core.config import settings
from .database import engine, Base
from .base import api_router


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def include_router(app: FastAPI):
    app.include_router(api_router)


def start_application() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)

    # Mount static files (for optional custom JS/CSS)
    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Run DB init at startup
    @app.on_event("startup")
    async def on_startup():
        await init_models()

    return app


app = start_application()
