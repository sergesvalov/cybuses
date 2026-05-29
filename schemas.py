from pydantic import BaseModel
from typing import Optional

class RouteCreate(BaseModel):
    provider: str
    name: str
    url: Optional[str] = None

class RouteBulkCreate(BaseModel):
    provider: str
    name: str
    text: str

class RouteUpdate(BaseModel):
    provider: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None

class DirectionCreate(BaseModel):
    route_id: int
    description: str
    day_type: str

class DirectionUpdate(BaseModel):
    description: Optional[str] = None
    day_type: Optional[str] = None

class DepartureCreate(BaseModel):
    direction_id: int
    time: str
    note_symbol: Optional[str] = None
    note_text: Optional[str] = None

class DepartureUpdate(BaseModel):
    time: Optional[str] = None
    note_symbol: Optional[str] = None
    note_text: Optional[str] = None
