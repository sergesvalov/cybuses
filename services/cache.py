import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from database import AsyncSessionLocal
from models import Route, Direction, Departure

logger = logging.getLogger("cache")


class CacheManager:
    def __init__(self):
        self._updating = False
        self._update_event = None
        self._cached_data = None
        self._last_updated = None
        self._lock = asyncio.Lock()

    def get_last_updated(self) -> str:
        """Returns ISO string of the last cache update timestamp."""
        return self._last_updated.isoformat() if self._last_updated else ""

    def _get_event(self):

        if self._update_event is None:
            self._update_event = asyncio.Event()
            self._update_event.set()
        return self._update_event

    async def wait_for_update(self):
        await self._get_event().wait()

    def load_from_disk(self):
        """Deprecated no-op kept for backwards compatibility."""
        pass

    async def update_cache(self, data, has_errors=False):
        """Updates the database with new scraped data and refreshes in-memory cache."""
        if not data:
            logger.warning("Update returned empty data. Preserving existing cache.")
            return

        valid_items = [d for d in data if not d.get('hasError')]
        if valid_items:
            self._cached_data = valid_items
            self._last_updated = datetime.now(timezone.utc)

        try:
            async with AsyncSessionLocal() as session:
                # Pre-fetch existing routes with directions to minimize DB roundtrips
                stmt = select(Route).options(selectinload(Route.directions))
                res = await session.execute(stmt)
                existing_routes = res.scalars().all()
                route_map = {(r.provider, r.name): r for r in existing_routes}

                for item in data:
                    if item.get('hasError'):
                        logger.info(f"Skipping update for {item.get('name')} due to scraper error, preserving existing data.")
                        continue

                    prov = item['prov']
                    name = item['name']
                    url = item.get('url')
                    desc = item['desc']
                    day_type = item['type']

                    # 1. Find or create Route
                    route = route_map.get((prov, name))
                    if not route:
                        route = Route(provider=prov, name=name, url=url)
                        session.add(route)
                        await session.flush()
                        route_map[(prov, name)] = route
                    elif url and route.url != url:
                        route.url = url

                    # 2. Find or create Direction
                    direction = None
                    if hasattr(route, 'directions') and route.directions:
                        for d in route.directions:
                            if d.description == desc and d.day_type == day_type:
                                direction = d
                                break

                    if direction:
                        # Clear old departures for this direction
                        await session.execute(delete(Departure).where(Departure.direction_id == direction.id))
                    else:
                        direction = Direction(route_id=route.id, description=desc, day_type=day_type)
                        session.add(direction)
                        await session.flush()
                        if not hasattr(route, 'directions') or route.directions is None:
                            route.directions = []
                        route.directions.append(direction)

                    # 3. Add new departures
                    notes_dict = item.get('notes') or {}
                    for t in item['times']:
                        sym = t.get('n') or ""
                        note_txt = t.get('note_txt') or notes_dict.get(sym, '')
                        dep = Departure(
                            direction_id=direction.id,
                            time=t['t'],
                            note_symbol=sym if sym else None,
                            note_text=note_txt if note_txt else None
                        )
                        session.add(dep)

                await session.commit()
                self._last_updated = datetime.now(timezone.utc)
                logger.info(f"Cache updated in DB. Processed {len(data)} items.")

                # Refresh in-memory cache directly from DB
                await self.get_data(force_refresh=True)
        except Exception as e:
            logger.warning(f"Database error or unavailable ({e}). Using in-memory cache.")



    async def get_data(self, force_refresh=False):
        """Returns normalized route data from fast memory cache, fallback to database."""
        if self._cached_data is not None and not force_refresh:
            return self._cached_data

        async with self._lock:
            # Double check after acquiring lock
            if self._cached_data is not None and not force_refresh:
                return self._cached_data

            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(Route).options(
                        selectinload(Route.directions).selectinload(Direction.departures)
                    )
                    result = await session.execute(stmt)
                    routes = result.scalars().all()

                    formatted = []
                    for r in routes:
                        for d in r.directions:
                            if not d.description or d.description == "Сбой загрузки расписания" or "\ufffd" in d.description:
                                continue

                            times = []
                            notes = {}
                            for dep in d.departures:
                                sym = dep.note_symbol or ""
                                txt = dep.note_text or ""
                                times.append({
                                    "t": dep.time,
                                    "n": sym,
                                    "f": f"{dep.time}{sym}",
                                    "note_txt": txt
                                })
                                if sym and txt:
                                    notes[sym] = txt

                            times.sort(key=lambda x: x["t"])
                            formatted.append({
                                "prov": r.provider,
                                "name": r.name,
                                "desc": d.description,
                                "type": d.day_type,
                                "url": r.url,
                                "times": times,
                                "notes": notes
                            })

                    self._cached_data = formatted
                    if self._last_updated is None and formatted:
                        self._last_updated = datetime.now(timezone.utc)
                    return self._cached_data
            except Exception as e:
                logger.error(f"Failed to fetch data from DB: {e}")
                return self._cached_data or []

    def set_updating(self, is_updating: bool):
        self._updating = is_updating
        event = self._get_event()
        if is_updating:
            event.clear()
        else:
            event.set()

    def is_updating(self):
        return self._updating

    def invalidate_memory_cache(self):
        """Explicitly clear the in-memory cache (e.g. after admin edits)."""
        self._cached_data = None
