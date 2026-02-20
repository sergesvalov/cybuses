import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router, cache_manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Ensure static directory exists
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Triggered on server startup"""
    cache_manager.load_from_disk()

@app.get("/")
async def index():
    return FileResponse("templates/index.html")