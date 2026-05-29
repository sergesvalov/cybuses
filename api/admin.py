import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from database import AsyncSessionLocal
from models import Route, Direction, Departure
from schemas import RouteCreate, RouteUpdate, DirectionCreate, DirectionUpdate, DepartureCreate, DepartureUpdate

router = APIRouter()
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- DATA DUMP ---
@router.get("/data")
async def get_all_data(username: str = Depends(verify_credentials)):
    """Returns the full database state with IDs for the admin panel."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Route).options(selectinload(Route.directions).selectinload(Direction.departures)))
        routes = result.scalars().all()
        return routes

# --- ROUTES ---
@router.post("/routes")
async def create_route(route: RouteCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = Route(**route.dict())
        session.add(db_route)
        await session.commit()
        await session.refresh(db_route)
        return db_route

import re
from schemas import RouteBulkCreate

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
                prev = lines[i-1]
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
        # Create Route
        db_route = Route(provider=payload.provider, name=payload.name)
        session.add(db_route)
        await session.flush()
        
        for b in blocks:
            d_desc = b["direction"]
            # Check if this direction+day already created for this route (just in case)
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
        return db_route

@router.put("/routes/{route_id}")
async def update_route(route_id: int, route: RouteUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = await session.get(Route, route_id)
        if not db_route:
            raise HTTPException(status_code=404, detail="Route not found")
        for key, value in route.dict(exclude_unset=True).items():
            setattr(db_route, key, value)
        await session.commit()
        await session.refresh(db_route)
        return db_route

@router.delete("/routes/{route_id}")
async def delete_route(route_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_route = await session.get(Route, route_id)
        if not db_route:
            raise HTTPException(status_code=404, detail="Route not found")
        await session.delete(db_route)
        await session.commit()
        return {"status": "success"}

# --- DIRECTIONS ---
@router.post("/directions")
async def create_direction(direction: DirectionCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = Direction(**direction.dict())
        session.add(db_dir)
        await session.commit()
        await session.refresh(db_dir)
        return db_dir

@router.put("/directions/{direction_id}")
async def update_direction(direction_id: int, direction: DirectionUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = await session.get(Direction, direction_id)
        if not db_dir:
            raise HTTPException(status_code=404, detail="Direction not found")
        for key, value in direction.dict(exclude_unset=True).items():
            setattr(db_dir, key, value)
        await session.commit()
        await session.refresh(db_dir)
        return db_dir

@router.delete("/directions/{direction_id}")
async def delete_direction(direction_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dir = await session.get(Direction, direction_id)
        if not db_dir:
            raise HTTPException(status_code=404, detail="Direction not found")
        await session.delete(db_dir)
        await session.commit()
        return {"status": "success"}

# --- DEPARTURES ---
@router.post("/departures")
async def create_departure(departure: DepartureCreate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = Departure(**departure.dict())
        session.add(db_dep)
        await session.commit()
        await session.refresh(db_dep)
        return db_dep

@router.put("/departures/{departure_id}")
async def update_departure(departure_id: int, departure: DepartureUpdate, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = await session.get(Departure, departure_id)
        if not db_dep:
            raise HTTPException(status_code=404, detail="Departure not found")
        for key, value in departure.dict(exclude_unset=True).items():
            setattr(db_dep, key, value)
        await session.commit()
        await session.refresh(db_dep)
        return db_dep

@router.delete("/departures/{departure_id}")
async def delete_departure(departure_id: int, username: str = Depends(verify_credentials)):
    async with AsyncSessionLocal() as session:
        db_dep = await session.get(Departure, departure_id)
        if not db_dep:
            raise HTTPException(status_code=404, detail="Departure not found")
        await session.delete(db_dep)
        await session.commit()
        return {"status": "success"}
