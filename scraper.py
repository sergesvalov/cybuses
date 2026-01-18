import json
import os
from fastapi import FastAPI
from scraper import get_all_data

app = FastAPI()
CACHE_FILE = "bus_cache.json"

@app.get("/")
def read_root():
    return {"status": "Bus Service API is online", "endpoints": "/api/buses"}

@app.get("/api/status")
def health_check():
    """Used by Jenkins/Docker for health checks"""
    return {"status": "ok"}

@app.get("/api/buses")
def get_buses():
    """
    Returns the cached data. If cache is missing, triggers a scrape.
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return get_all_data()
    else:
        return get_all_data()

@app.post("/api/refresh")
def force_refresh():
    """
    Manually triggers the scraper to update data.
    """
    return get_all_data()

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 is mandatory for Docker networking
    uvicorn.run(app, host="0.0.0.0", port=8000)