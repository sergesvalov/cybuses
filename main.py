import json
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_all_data_async
from app_html import HTML_TEMPLATE

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

CACHE_FILE = "bus_cache.json"
UPDATING = False

def load_cache():
    """Loads data from the JSON cache file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except: 
            return None
    return None

async def update_task():
    """Background task to update the cache asynchronously."""
    global UPDATING
    if UPDATING: return
    UPDATING = True
    try:
        # Run the async scraper
        data = await get_all_data_async()
        
        # Atomic write to avoid corruption
        tmp = CACHE_FILE + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CACHE_FILE)
        print(">>> Cache Updated Successfully")
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        UPDATING = False

@app.get("/", response_class=HTMLResponse)
def index():
    """Returns the frontend HTML."""
    return HTML_TEMPLATE

@app.get("/api/data")
async def get_data(bt: BackgroundTasks):
    """Returns bus data. Triggers update if cache is missing."""
    data = load_cache()
    if not data and not UPDATING: 
        bt.add_task(update_task)
        return []
    return data or []

@app.post("/api/refresh")
async def refresh(bt: BackgroundTasks):
    """Force triggers a cache update."""
    if not UPDATING: 
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}

@app.get("/api/status")
def status():
    """Checks if an update is currently in progress."""
    return {"updating": UPDATING}