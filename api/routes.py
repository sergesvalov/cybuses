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
        data = await scraper_service.get_all_data()
        cache_manager.update_cache(data)
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        cache_manager.set_updating(False)

@router.get("/data")
async def get_data(bt: BackgroundTasks):
    """Returns data from memory. If empty and not updating - triggers update."""
    # If memory is empty and we are not currently updating - kick off the scraper
    if not cache_manager.get_data() and not cache_manager.is_updating(): 
        bt.add_task(update_task)
    
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
