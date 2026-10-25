import re
import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from database import AsyncSessionLocal
from models import Route, Direction, Departure
from schemas import (
    RouteCreate, RouteBulkCreate, RouteUpdate,
    DirectionCreate, DirectionUpdate,
    DepartureCreate, DepartureUpdate
)
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from api.routes import cache_manager

logger = logging.getLogger("api.admin")
router = APIRouter()
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def model_to_dict(model_instance, exclude_unset=False):
    """Compatibility helper for Pydantic v1 and v2."""
    if hasattr(model_instance, "model_dump"):
        return model_instance.model_dump(exclude_unset=exclude_unset)
    return model_instance.dict(exclude_unset=exclude_unset)


# --- DATA DUMP ---
@router.get("/data")
async def get_all_data(username: str = Depends(verify_credentials)):
    """Returns the full database state with IDs formatted for the admin panel."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Route).options(
                selectinload(Route.directions).selectinload(Direction.departures)
            )
        )
        routes = result.scalars().all()
        # Explicit serialization to prevent lazy-loading or detached instance errors
        serialized = []
        for r in routes:
            dirs = []
            for d in (r.directions or []):
                deps = [
                    {
                        "id": dep.id,
                        "direction_id": dep.direction_id,
                        "time": dep.time,
                        "note_symbol": dep.note_symbol,
                        "note_text": dep.note_text
                    }
                    for dep in (d.departures or [])
                ]
                dirs.append({
                    "id": d.id,
                    "route_id": d.route_id,
                    "description": d.description,
                    "day_type": d.day_type,
                    "departures": deps
                })
            serialized.append({
                "id": r.id,
                "provider": r.provider,
                "name": r.name,
                "url": r.url,
                "directions": dirs
            })
        return serialized


# --- ROUTES ---
@router.post("/routes")
async def create_route(route: RouteCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = Route(**model_to_dict(route))
        session.add(db_route)
        await session.commit()
        await session.refresh(db_route)
        cache_manager.invalidate_memory_cache()
        return db_route


@router.post("/routes/bulk")
async def create_route_bulk(payload: RouteBulkCreate, username: str = Depends(verify_credentials)):
    """Parses raw text schedules and creates a route with its directions and departures."""
    lines = [line.strip() for line in payload.text.split('\n') if line.strip()]

    blocks = []
    current_direction = "Unknown"
    current_day = "all"
    notes_by_dir = {}
    time_pattern = re.compile(r'(\d{1,2}:\d{2})\s*([*A-Za-z]*)')

    for i, line in enumerate(lines):
        low = line.lower()
        if line.startswith('*'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                notes_by_dir.setdefault(current_direction, {})[parts[0]] = parts[1]
            continue

        if any(d in low for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'daily', 'every day', 'будни', 'выходные']):
            current_day = line
            if i > 0:
                prev = lines[i - 1]
                if not time_pattern.search(prev) and not prev.startswith('*') and 'bus stops' not in prev.lower() and 'ticket' not in prev.lower():
                    current_direction = prev
            continue

        matches = time_pattern.findall(line)
        if matches:
            blocks.append({
                "direction": current_direction,
                "day_type": current_day,
                "times": [{"t": m[0], "sym": m[1]} for m in matches]
            })

    async with AsyncSessionLocal() as session:
        db_route = Route(provider=payload.provider, name=payload.name)
        session.add(db_route)
        await session.flush()

        for b in blocks:
            d_desc = b["direction"]
            db_dir = Direction(route_id=db_route.id, description=d_desc, day_type=b["day_type"])
            session.add(db_dir)
            await session.flush()

            d_notes = notes_by_dir.get(d_desc, {})
            for t in b["times"]:
                sym = t["sym"] if t["sym"] else None
                db_dep = Departure(
                    direction_id=db_dir.id,
                    time=t["t"],
                    note_symbol=sym,
                    note_text=d_notes.get(sym) if sym else None
                )
                session.add(db_dep)

        await session.commit()
        await session.refresh(db_route)
        cache_manager.invalidate_memory_cache()
        return db_route


@router.put("/routes/{route_id}")
async def update_route(route_id: int, route: RouteUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = await session.get(Route, route_id)
        if not db_route:
            raise HTTPException(status_code=404, detail="Route not found")
        for key, value in model_to_dict(route, exclude_unset=True).items():
            setattr(db_route, key, value)
        await session.commit()
        await session.refresh(db_route)
        cache_manager.invalidate_memory_cache()
        return db_route


@router.delete("/routes/{route_id}")
async def delete_route(route_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = await session.get(Route, route_id)
        if not db_route:
            raise HTTPException(status_code=404, detail="Route not found")
        await session.delete(db_route)
        await session.commit()
        cache_manager.invalidate_memory_cache()
        return {"status": "success"}


# --- DIRECTIONS ---
@router.post("/directions")
async def create_direction(direction: DirectionCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = Direction(**model_to_dict(direction))
        session.add(db_dir)
        await session.commit()
        await session.refresh(db_dir)
        cache_manager.invalidate_memory_cache()
        return db_dir


@router.put("/directions/{direction_id}")
async def update_direction(direction_id: int, direction: DirectionUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = await session.get(Direction, direction_id)
        if not db_dir:
            raise HTTPException(status_code=404, detail="Direction not found")
        for key, value in model_to_dict(direction, exclude_unset=True).items():
            setattr(db_dir, key, value)
        await session.commit()
        await session.refresh(db_dir)
        cache_manager.invalidate_memory_cache()
        return db_dir


@router.delete("/directions/{direction_id}")
async def delete_direction(direction_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = await session.get(Direction, direction_id)
        if not db_dir:
            raise HTTPException(status_code=404, detail="Direction not found")
        await session.delete(db_dir)
        await session.commit()
        cache_manager.invalidate_memory_cache()
        return {"status": "success"}


# --- DEPARTURES ---
@router.post("/departures")
async def create_departure(departure: DepartureCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = Departure(**model_to_dict(departure))
        session.add(db_dep)
        await session.commit()
        await session.refresh(db_dep)
        cache_manager.invalidate_memory_cache()
        return db_dep


@router.put("/departures/{departure_id}")
async def update_departure(departure_id: int, departure: DepartureUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = await session.get(Departure, departure_id)
        if not db_dep:
            raise HTTPException(status_code=404, detail="Departure not found")
        for key, value in model_to_dict(departure, exclude_unset=True).items():
            setattr(db_dep, key, value)
        await session.commit()
        await session.refresh(db_dep)
        cache_manager.invalidate_memory_cache()
        return db_dep


@router.delete("/departures/{departure_id}")
async def delete_departure(departure_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = await session.get(Departure, departure_id)
        if not db_dep:
            raise HTTPException(status_code=404, detail="Departure not found")
        await session.delete(db_dep)
        await session.commit()
        cache_manager.invalidate_memory_cache()
        return {"status": "success"}
