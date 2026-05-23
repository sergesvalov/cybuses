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
        cache_manager.update_cache(data, has_errors)
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        cache_manager.set_updating(False)

@router.get("/data")
async def get_data(bt: BackgroundTasks):
    """Returns data from memory. If empty, waits for update."""
    if not cache_manager.get_data():
        if not cache_manager.is_updating(): 
            # If nothing triggered the update yet, do it now and wait
            await update_task()
        else:
            # If it's already updating, wait for it to finish
            import asyncio
            while cache_manager.is_updating():
                await asyncio.sleep(0.5)
    
    return cache_manager.get_data()

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
