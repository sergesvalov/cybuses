import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from database import AsyncSessionLocal
from models import Route, Direction, Departure

class CacheManager:
    def __init__(self):
        self._updating = False
        self._update_event = None

    def _get_event(self):
        if self._update_event is None:
            self._update_event = asyncio.Event()
            self._update_event.set()
        return self._update_event

    async def wait_for_update(self):
        await self._get_event().wait()

    def load_from_disk(self):
        # Deprecated. No-op for compatibility.
        print(">>> load_from_disk() called, ignoring since we use PostgreSQL")

    async def update_cache(self, data, has_errors=False):
        """Updates the postgres database with new data."""
        if not data:
            print(">>> Update returned empty data. Keeping old cache.")
            return

        async with AsyncSessionLocal() as session:
            try:
                for item in data:
                    if item.get('hasError'):
                        print(f"Skipping update for {item.get('name')} due to scraper error, preserving old data.")
                        continue

                    # Find or create Route
                    result = await session.execute(select(Route).where(Route.name == item['name'], Route.provider == item['prov']))
                    route = result.scalars().first()
                    if not route:
                        route = Route(provider=item['prov'], name=item['name'], url=item.get('url'))
                        session.add(route)
                        await session.flush()
                    else:
                        if item.get('url') and route.url != item['url']:
                            route.url = item['url']
                    
                    # Find or create Direction
                    result = await session.execute(select(Direction).where(Direction.route_id == route.id, Direction.description == item['desc'], Direction.day_type == item['type']))
                    direction = result.scalars().first()
                    if direction:
                        # Clear old departures
                        await session.execute(delete(Departure).where(Departure.direction_id == direction.id))
                    else:
                        direction = Direction(route_id=route.id, description=item['desc'], day_type=item['type'])
                        session.add(direction)
                        await session.flush()
                    
                    # Add new departures
                    for t in item['times']:
                        note_txt = t.get('note_txt') or item.get('notes', {}).get(t.get('n', ''), '')
                        dep = Departure(direction_id=direction.id, time=t['t'], note_symbol=t.get('n', ''), note_text=note_txt)
                        session.add(dep)
                
                await session.commit()
                print(f">>> Cache Updated Successfully in PostgreSQL. Processed {len(data)} routes/directions.")
            except Exception as e:
                await session.rollback()
                print(f"Error saving cache to DB: {e}")

    async def get_data(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Route).options(selectinload(Route.directions).selectinload(Direction.departures)))
            routes = result.scalars().all()
            
            data = []
            for r in routes:
                for d in r.directions:
                    times = []
                    notes = {}
                    for dep in d.departures:
                        times.append({
                            "t": dep.time,
                            "n": dep.note_symbol,
                            "f": dep.time + dep.note_symbol,
                            "note_txt": dep.note_text
                        })
                        if dep.note_symbol and dep.note_text:
                            notes[dep.note_symbol] = dep.note_text
                    
                    times.sort(key=lambda x: x["t"])
                    if d.description == "Сбой загрузки расписания" or "\ufffd" in d.description:
                        continue
                        
                    data.append({
                        "prov": r.provider,
                        "name": r.name,
                        "desc": d.description,
                        "type": d.day_type,
                        "url": r.url,
                        "times": times,
                        "notes": notes
                    })
            return data

    def set_updating(self, is_updating: bool):
        self._updating = is_updating
        event = self._get_event()
        if is_updating:
            event.clear()
        else:
            event.set()

    def is_updating(self):
        return self._updating
