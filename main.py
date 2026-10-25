import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router, cache_manager, periodic_update, scraper_service
from api.admin import router as admin_router, verify_credentials
from database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifecycle manager: cleanly starts and shuts down services."""
    # 1. Warm up in-memory cache
    asyncio.create_task(cache_manager.get_data())

    # 2. Launch background periodic update loop
    update_task_handle = asyncio.create_task(periodic_update())

    yield

    # 3. Shutdown: gracefully cancel tasks and dispose connections
    update_task_handle.cancel()
    try:
        await update_task_handle
    except asyncio.CancelledError:
        pass
    except Exception:
        pass

    await scraper_service.close()
    await engine.dispose()


app = FastAPI(title="Cyprus Buses API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure static directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")


@app.get("/")
async def index():
    return FileResponse("templates/index.html")


@app.get("/admin")
async def admin(username: str = Depends(verify_credentials)):
    return FileResponse("templates/admin.html")