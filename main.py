import json
import os
from fastapi import FastAPI
# This import is correct here
from scraper import get_all_data

app = FastAPI()
CACHE_FILE = "bus_cache.json"

@app.get("/api/status")
def health_check():
    return {"status": "ok"}

@app.get("/api/buses")
def get_buses():
    """Returns cached bus data or triggers a new scrape if cache is missing."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_all_data()

@app.post("/api/refresh")
def refresh():
    """Force an immediate update of bus schedules."""
    return get_all_data()

if __name__ == "__main__":
    import uvicorn
    # Port 8000 is required for your Docker setup
    uvicorn.run(app, host="0.0.0.0", port=8000)