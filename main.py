import json, os, time
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_all_data
from app_html import HTML_TEMPLATE

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CACHE_FILE = "bus_cache.json"
UPDATING = False

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return None
    return None

def update_task():
    global UPDATING
    if UPDATING: return
    UPDATING = True
    try:
        data = get_all_data()
        tmp = CACHE_FILE + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CACHE_FILE)
        print(">>> Cache Updated")
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        UPDATING = False

@app.get("/api/data")
def get_data():
    data = load_cache()
    if not data and not UPDATING: 
        update_task()
        return load_cache() or []
    return data or []

@app.post("/api/refresh")
def refresh(bt: BackgroundTasks):
    if not UPDATING: 
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}

@app.get("/api/status")
def status(): return {"updating": UPDATING}

@app.get("/", response_class=HTMLResponse)
def index(): return HTML_TEMPLATE

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists(CACHE_FILE):
        try: update_task()
        except: pass
    uvicorn.run(app, host="0.0.0.0", port=8000)