import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, Response
from services.cache import CacheManager
from services.scraper import ScraperService

logger = logging.getLogger("api.routes")
router = APIRouter()

# Instantiate core services
cache_manager = CacheManager()
scraper_service = ScraperService()


async def update_task():
    """Background task: downloads fresh data, updates database and in-memory cache."""
    if cache_manager.is_updating():
        return
    cache_manager.set_updating(True)
    try:
        logger.info(">>> Starting scheduled scraper task...")
        data, has_errors = await scraper_service.get_all_data()
        await cache_manager.update_cache(data, has_errors)
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)
    finally:
        cache_manager.set_updating(False)


async def periodic_update():
    """Loops to update data periodically every hour."""
    while True:
        try:
            logger.info(">>> Running scheduled periodic update...")
            await update_task()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic update error: {e}")
        # Sleep for 1 hour (3600 seconds)
        await asyncio.sleep(3600)


@router.get("/data")
async def get_data(response: Response):
    """Returns route data from high-speed in-memory cache. If empty, waits for update."""
    data = await cache_manager.get_data()
    if not data:
        if not cache_manager.is_updating():
            await update_task()
        else:
            await cache_manager.wait_for_update()
        data = await cache_manager.get_data()

    # Short client cache header for responsiveness while saving bandwidth
    response.headers["Cache-Control"] = "public, max-age=30"
    last_updated = cache_manager.get_last_updated()
    if last_updated:
        response.headers["X-Last-Updated"] = last_updated
    return data


@router.post("/refresh")
async def refresh(bt: BackgroundTasks):
    """Manual refresh triggered by user."""
    if not cache_manager.is_updating():
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}


@router.get("/status")
def status():
    """Returns the current updating status."""
    return {"updating": cache_manager.is_updating()}
