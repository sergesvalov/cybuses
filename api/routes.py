from fastapi import APIRouter, BackgroundTasks
from services.cache import CacheManager
from services.scraper import ScraperService

router = APIRouter()

# Instantiate core services
cache_manager = CacheManager()
scraper_service = ScraperService()

async def update_task():
    """Background task: downloads fresh data, updates memory and disk caches"""
    if cache_manager.is_updating():
        return
    cache_manager.set_updating(True)
    try:
        print(">>> Starting update task...")
        data, has_errors = await scraper_service.get_all_data()
        await cache_manager.update_cache(data, has_errors)
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        cache_manager.set_updating(False)

async def periodic_update():
    """Loops infinitely to update data periodically."""
    while True:
        print(">>> Running scheduled periodic update...")
        await update_task()
        # Sleep for 1 hour (3600 seconds) before the next update
        await asyncio.sleep(3600)

@router.get("/data")
async def get_data(bt: BackgroundTasks):
    """Returns data from memory. If empty, waits for update."""
    data = await cache_manager.get_data()
    if not data:
        if not cache_manager.is_updating(): 
            # If nothing triggered the update yet, do it now and wait
            await update_task()
        else:
            # If it's already updating, wait for it to finish
            await cache_manager.wait_for_update()
        data = await cache_manager.get_data()
    
    return data

@router.post("/refresh")
async def refresh(bt: BackgroundTasks):
    """Manual refresh triggered by the user."""
    if not cache_manager.is_updating(): 
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}

@router.get("/status")
def status():
    """Returns the current updating status."""
    return {"updating": cache_manager.is_updating()}
