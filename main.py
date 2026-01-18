import json
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_all_data_async

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

CACHE_FILE = "bus_cache.json"
# Глобальная переменная для хранения расписания в оперативной памяти
MEMORY_CACHE = []
UPDATING = False

def load_cache_from_disk():
    """Читает файл с диска и сохраняет в глобальную переменную"""
    global MEMORY_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: 
                MEMORY_CACHE = json.load(f)
            print(f">>> Cache loaded from disk: {len(MEMORY_CACHE)} routes")
        except Exception as e:
            print(f"Error loading cache from disk: {e}")
            MEMORY_CACHE = []
    else:
        print(">>> No cache file found on disk.")

@app.on_event("startup")
async def startup_event():
    """Запускается при старте сервера"""
    load_cache_from_disk()

async def update_task():
    """Фоновая задача: скачивает данные, обновляет память и диск"""
    global UPDATING, MEMORY_CACHE
    if UPDATING: return
    UPDATING = True
    try:
        print(">>> Starting update task...")
        # Скачиваем свежие данные
        data = await get_all_data_async()
        
        # ВАЖНО: Если парсер вернул пустой список (ошибка сети), не затираем старый кэш!
        if data:
            # 1. Обновляем память (мгновенно для пользователей)
            MEMORY_CACHE = data
            
            # 2. Сохраняем на диск (чтобы данные пережили перезагрузку)
            tmp = CACHE_FILE + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f: 
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CACHE_FILE)
            print(f">>> Cache Updated Successfully. Routes: {len(data)}")
        else:
            print(">>> Update returned empty data. Keeping old cache.")
            
    except Exception as e:
        print(f"Update failed: {e}")
    finally: 
        UPDATING = False

@app.get("/")
async def index():
    return FileResponse("templates/index.html")

@app.get("/api/data")
async def get_data(bt: BackgroundTasks):
    """Отдает данные из памяти. Если пусто — запускает обновление."""
    global MEMORY_CACHE
    
    # Если память пуста и мы сейчас не обновляемся — пнуть скрапер
    if not MEMORY_CACHE and not UPDATING: 
        bt.add_task(update_task)
    
    return MEMORY_CACHE

@app.post("/api/refresh")
async def refresh(bt: BackgroundTasks):
    if not UPDATING: 
        bt.add_task(update_task)
        return {"status": "started"}
    return {"status": "busy"}

@app.get("/api/status")
def status():
    return {"updating": UPDATING}