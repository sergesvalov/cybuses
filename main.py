import json
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse # Импортируем FileResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_all_data_async

# Строка импорта app_html больше не нужна!

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

CACHE_FILE = "bus_cache.json"
UPDATING = False

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except: return None
    return None

async def update_task():
    global UPDATING
    if UPDATING: return
    UPDATING = True
    try:
        data = await get_all_data_async()
        tmp = CACHE_FILE + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CACHE_FILE)
        print(">>> Cache Updated Successfully")
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        UPDATING = False

# --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
@app.get("/")
async def index():
    # Отдаем файл из папки templates
    return FileResponse("templates/index.html")
# -----------------------

@app.get("/api/data")
async def get_data(bt: BackgroundTasks):
    data = load_cache()
    if not data and not UPDATING: 
        bt.add_task(update_task)
        return []
    return data or []

@app.post("/api/refresh")
async def refresh(bt: BackgroundTasks):
    if not UPDATING: 
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}

@app.get("/api/status")
def status():
    return {"updating": UPDATING}