from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)
    name = Column(String, index=True)
    url = Column(String)

    directions = relationship("Direction", back_populates="route", cascade="all, delete-orphan")

class Direction(Base):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    description = Column(String)
    day_type = Column(String)

    route = relationship("Route", back_populates="directions")
    departures = relationship("Departure", back_populates="direction", cascade="all, delete-orphan")

class Departure(Base):
    __tablename__ = "departures"

    id = Column(Integer, primary_key=True, index=True)
    direction_id = Column(Integer, ForeignKey("directions.id"), nullable=False)
    time = Column(String)
    note_symbol = Column(String)
    note_text = Column(String)

    direction = relationship("Direction", back_populates="departures")
