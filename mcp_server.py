"""
MCP Server — Intercity Buses Cyprus
====================================
Standalone MCP server exposing intercity bus schedule data
(Limassol, Nicosia, Larnaca ↔ Paphos) for AI assistants.

Run:
    python mcp_server.py

Transport: sse (port 8999, path /sse)
Connect your MCP client to: http://<host>:8999/sse

⚠️ This is NOT a web page! Do NOT open in browser.
   MCP is a machine-to-machine protocol (POST-based).
   Use an MCP client (Python SDK, Claude Desktop, etc.)
"""

import os
import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta, timezone
from typing import Optional


def _get_cyprus_now() -> datetime:
    """Returns current datetime in Cyprus timezone with fallback if IANA tzdata is missing on Windows."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Asia/Nicosia"))
    except Exception:
        now_utc = datetime.now(timezone.utc)
        month = now_utc.month
        offset_hours = 3 if 4 <= month <= 10 else 2
        return now_utc + timedelta(hours=offset_hours)


# --- Reuse project internals ---
from config import ROUTES, MCP_HOST, MCP_PORT
from services.cache import CacheManager
from services.scraper import ScraperService

os.environ["FASTMCP_HOST"] = MCP_HOST
os.environ["FASTMCP_PORT"] = str(MCP_PORT)

try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ImportError:
        FastMCP = None

# ── Logging setup ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("mcp-cybuses")

# ── Server setup ────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="CyBuses Intercity",
    host=MCP_HOST,
    port=MCP_PORT,
    instructions=(
        "This MCP server provides real-time intercity bus schedules for Cyprus. "
        "Routes: Paphos ↔ Limassol, Paphos ↔ Nicosia, Paphos ↔ Larnaca, Nicosia ↔ Limassol, Larnaca ↔ Limassol, Larnaca ↔ Paralimni, Nicosia ↔ Paralimni, Paphos ↔ Paralimni. "
        "Use get_intercity_routes to list routes, get_schedule to see full timetable, "
        "and get_nearest_bus to find the next departure."
    ),
    sse_path="/sse"
)

# ── Simple in-memory cache (TTL = 5 min) ────────────────────────────────────

cache_manager = CacheManager()
scraper_service = ScraperService()

ALL_ROUTES = ROUTES


async def _fetch_schedule(route_key: str) -> list[dict]:
    """Fetch schedule from shared cache, fallback to scraper."""
    data = await cache_manager.get_data()
    
    info = ALL_ROUTES[route_key]
    route_name = info['name']
    
    if data:
        # Filter for the requested route_key
        route_data = [d for d in data if d.get('prov') == info.get('provider') and d.get('name') == route_name]
        if route_data:
            log.info(f"Cache HIT for '{route_key}'")
            return route_data

    log.info(f"Cache MISS for '{route_key}', fetching from website...")
    try:
        async with aiohttp.ClientSession() as session:
            route_data = await scraper_service.fetch_route(session, route_key, info)
        log.info(f"Fetched '{route_key}': {len(route_data)} direction(s)")
        
        return route_data
    except Exception as e:
        log.error(f"Failed to fetch '{route_key}': {e}")
        return []


def _format_schedule_text(data: list[dict]) -> str:
    """Format parsed schedule data into a human-readable string."""
    if not data:
        return "Расписание не найдено. Попробуйте позже."

    lines = []
    for direction in data:
        lines.append(f"🚌 {direction['desc']}")
        if direction.get("price"):
            lines.append(f"   💶 Цена: {direction['price']}")
        if direction.get("duration"):
            lines.append(f"   ⏱ В пути: {direction['duration']}")

        times = direction.get("times", [])
        if not times:
            lines.append("   ❌ Нет данных о времени")
            continue

        time_parts = []
        for t in times:
            entry = t["t"]
            if t.get("note_txt"):
                entry += f" ({t['note_txt']})"
            elif t.get("n"):
                entry += t["n"]
            time_parts.append(entry)

        lines.append("   " + ", ".join(time_parts))

        # Footnotes
        notes = direction.get("notes", {})
        if notes:
            for sym, note in notes.items():
                lines.append(f"   {sym} — {note}")

        lines.append("")

    return "\n".join(lines).strip()


# ── MCP Tools ────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_routes() -> str:
    """
    Возвращает список доступных маршрутов автобусов (Intercity и Osypa).
    Используй этот инструмент чтобы узнать какие маршруты доступны.
    """
    log.info("Tool called: get_routes")
    lines = ["📋 Доступные маршруты:", ""]
    for key, info in ALL_ROUTES.items():
        lines.append(f"• {info['name']} — route_key: \"{key}\"")
        lines.append(f"  URL: {info['url']}")
    lines.append("")
    lines.append("Используй get_schedule(route) или get_nearest_bus(route) для подробностей.")
    return "\n".join(lines)


@mcp.tool()
async def get_intercity_routes() -> str:
    """
    Возвращает список доступных междугородних маршрутов Кипра (псевдоним get_routes).
    """
    return await get_routes()


@mcp.tool()
async def get_schedule(route: str) -> str:
    """
    Возвращает полное расписание автобусов для указанного маршрута.
    Включает оба направления, времена отправления, цены и примечания.

    Args:
        route: Ключ маршрута — "limassol", "nicosia", "larnaca", "nicosia_limassol", "larnaca_limassol", "larnaca_paralimni", "nicosia_paralimni" или "paphos_paralimni"
    """
    log.info(f"Tool called: get_schedule(route='{route}')")
    route = route.lower().strip()
    if route not in ALL_ROUTES:
        available = ", ".join(ALL_ROUTES.keys())
        log.warning(f"Unknown route '{route}', available: {available}")
        return f"❌ Неизвестный маршрут '{route}'. Доступные: {available}"

    data = await _fetch_schedule(route)
    header = f"📅 Расписание: {ALL_ROUTES[route]['name']}\n"
    result_text = header + _format_schedule_text(data)
    snippet = result_text[:100].replace('\n', ' ')
    log.info(f"get_schedule returning {len(result_text)} chars. Snippet: {snippet}...")
    return result_text


@mcp.tool()
async def get_nearest_bus(
    route: str,
    direction: Optional[str] = None,
) -> str:
    """
    Находит ближайший автобус от текущего времени для указанного маршрута.
    Возвращает время отправления и сколько минут до него осталось.

    Args:
        route: Ключ маршрута — "limassol", "nicosia", "larnaca", "nicosia_limassol", "larnaca_limassol", "larnaca_paralimni", "nicosia_paralimni" или "paphos_paralimni"
        direction: Направление — "dir1" (или "from_paphos") / "dir2" (или "to_paphos"). 
                   Если не указано, показывает ближайшие для обоих направлений.
    """
    log.info(f"Tool called: get_nearest_bus(route='{route}', direction='{direction}')")
    route = route.lower().strip()
    if route not in ALL_ROUTES:
        available = ", ".join(ALL_ROUTES.keys())
        log.warning(f"Unknown route '{route}', available: {available}")
        return f"❌ Неизвестный маршрут '{route}'. Доступные: {available}"

    data = await _fetch_schedule(route)
    if not data:
        return "❌ Не удалось загрузить расписание."

    now = _get_cyprus_now()
    now_str = now.strftime("%H:%M")
    results = []

    for dir_data in data:
        desc = dir_data["desc"]

        # Filter by direction if specified
        if direction:
            direction = direction.lower().strip()
            if 'city1' in ALL_ROUTES[route] and 'city2' in ALL_ROUTES[route]:
                city1_name = ALL_ROUTES[route]['city1'].title()
                city2_name = ALL_ROUTES[route]['city2'].title()
                
                if direction in ("dir1", "from_paphos") and "➝" in desc and desc.startswith(city1_name):
                    pass  # match
                elif direction in ("dir2", "to_paphos") and "➝" in desc and desc.startswith(city2_name):
                    pass  # match
                else:
                    continue
            else:
                if direction not in desc.lower():
                    continue

        times = dir_data.get("times", [])
        if not times:
            continue

        # Find next departure
        upcoming = []
        for t in times:
            t_str = t["t"]
            if t_str > now_str:
                upcoming.append(t)

        if upcoming:
            next_bus = upcoming[0]
            t_parts = next_bus["t"].split(":")
            dep_time = now.replace(hour=int(t_parts[0]), minute=int(t_parts[1]), second=0)
            diff = dep_time - now
            minutes_left = int(diff.total_seconds() // 60)

            note = ""
            if next_bus.get("note_txt"):
                note = f" ({next_bus['note_txt']})"

            duration_text = ""
            if dir_data.get("duration"):
                duration_text = f"\n   ⏱ В пути: {dir_data['duration']}"

            log.info(f"Next bus {desc}: {next_bus['t']} (in {minutes_left} min)")
            results.append(
                f"🚌 {desc}\n"
                f"   ⏰ Ближайший: {next_bus['t']}{note}\n"
                f"   ⏳ Через {minutes_left} мин{duration_text}"
            )

            # Show also next 2 buses after that
            if len(upcoming) > 1:
                extras = [u["t"] for u in upcoming[1:3]]
                results.append(f"   Следующие: {', '.join(extras)}")
        else:
            results.append(f"🚌 {desc}\n   ❌ На сегодня рейсов больше нет")

        results.append("")

    if not results:
        return "❌ Нет данных для указанного направления."

    header = f"🕐 Ближайшие автобусы ({now.strftime('%H:%M')}) — {ALL_ROUTES[route]['name']}\n\n"
    result_text = header + "\n".join(results).strip()
    snippet = result_text[:100].replace('\n', ' ')
    log.info(f"get_nearest_bus returning {len(result_text)} chars. Snippet: {snippet}...")
    return result_text


# ── Extended MCP Tools (Route Finder, Airport Transfers, Search) ──────────────

CITY_SYNONYMS = {
    "paphos": ["paphos", "pafos", "пафос"],
    "limassol": ["limassol", "lemesos", "лимассол"],
    "nicosia": ["nicosia", "lefkosia", "никосия"],
    "larnaca": ["larnaca", "ларнака"],
    "paralimni": ["paralimni", "ayia napa", "agia napa", "паралимни", "айя-напа"],
    "paphos_airport": ["paphos airport", "pfo", "аэропорт пафос", "аэропорт пафоса"],
    "larnaca_airport": ["larnaca airport", "lca", "аэропорт ларнака", "аэропорт ларнаки"]
}


def _normalize_city_token(token: str) -> str:
    t_lower = token.lower().strip()
    for norm, syns in CITY_SYNONYMS.items():
        if any(s in t_lower for s in syns):
            return norm
    return t_lower


@mcp.tool()
async def find_bus(
    origin: str,
    destination: str,
    at_time: Optional[str] = None
) -> str:
    """
    Находит прямые автобусы между двумя пунктами на Кипре (города или аэропорты).
    Поддерживает названия на русском и английском (например, 'Пафос', 'Лимассол', 'Никосия', 'Ларнака', 'Аэропорт Пафос').

    Args:
        origin: Пункт отправления (например, 'Paphos', 'Лимассол', 'Larnaca Airport')
        destination: Пункт назначения (например, 'Nicosia', 'Пафос', 'Аэропорт Ларнака')
        at_time: Время отправления 'HH:MM' (если не указано, используется текущее время на Кипре)
    """
    log.info(f"Tool called: find_bus(origin='{origin}', destination='{destination}', at_time='{at_time}')")
    norm_origin = _normalize_city_token(origin)
    norm_dest = _normalize_city_token(destination)

    now = _get_cyprus_now()
    target_time_str = at_time.strip() if at_time else now.strftime("%H:%M")

    matched_results = []

    for route_key, info in ALL_ROUTES.items():
        route_data = await _fetch_schedule(route_key)
        for direction in route_data:
            desc = direction.get("desc", "").lower()
            name = direction.get("name", "").lower()
            combined = f"{name} {desc}"

            # Check directional match: "Source ➝ Destination"
            is_match = False
            if "➝" in desc or "→" in desc:
                parts = [p.strip() for p in desc.replace("→", "➝").split("➝")]
                src_part = parts[0]
                dst_part = parts[-1]

                origin_syns = CITY_SYNONYMS.get(norm_origin, [norm_origin])
                dest_syns = CITY_SYNONYMS.get(norm_dest, [norm_dest])

                match_src = any(s in src_part for s in origin_syns)
                match_dst = any(d in dst_part for d in dest_syns)
                if match_src and match_dst:
                    is_match = True
            else:
                # Airport shuttles or local routes
                origin_syns = CITY_SYNONYMS.get(norm_origin, [norm_origin])
                dest_syns = CITY_SYNONYMS.get(norm_dest, [norm_dest])
                if any(s in combined for s in origin_syns) and any(d in combined for d in dest_syns):
                    is_match = True

            if not is_match:
                continue

            times = direction.get("times", [])
            upcoming_times = []
            for t in times:
                t_str = t.get("t", "")
                if t_str >= target_time_str and t_str != "LINK":
                    note = f" ({t['note_txt']})" if t.get("note_txt") else (t.get("n") or "")
                    upcoming_times.append(f"{t_str}{note}")

            line_entry = [f"🚌 {direction.get('desc', name)} ({info['name']})"]
            if direction.get("price"):
                line_entry.append(f"   💶 Цена: {direction['price']}")
            if direction.get("duration"):
                line_entry.append(f"   ⏱ В пути: {direction['duration']}")

            if upcoming_times:
                sample = upcoming_times[:8]
                line_entry.append(f"   ⏰ Рейсы начиная с {target_time_str}: {', '.join(sample)}")
                if len(upcoming_times) > 8:
                    line_entry.append(f"      (всего {len(upcoming_times)} рейсов)")
            else:
                all_t = [t.get("t") for t in times if t.get("t") != "LINK"]
                if all_t:
                    line_entry.append(f"   ℹ️ После {target_time_str} рейсов нет. Все рейсы дня: {', '.join(all_t[:6])}...")
                else:
                    line_entry.append(f"   🔗 Ссылка на бронирование/расписание: {info['url']}")

            matched_results.append("\n".join(line_entry))

    if not matched_results:
        return (
            f"❌ Прямых рейсов между '{origin}' и '{destination}' не найдено.\n"
            f"Совет: попробуйте поиск с пересадкой (например, через Лимассол) или проверьте шаттлы в аэропорт через get_airport_transfers."
        )

    header = f"🎯 Найденные автобусы: {origin.title()} ➔ {destination.title()}\nВремя отправления: начиная с {target_time_str}\n\n"
    return header + "\n\n".join(matched_results)


@mcp.tool()
async def get_airport_transfers(
    airport: str,
    city: Optional[str] = None
) -> str:
    """
    Возвращает информацию о шаттлах и автобусах в аэропорты Кипра (Ларнака LCA или Пафос PFO).
    Показывает расписания Limassol Airport Express, Kapnos Airport Shuttle и OSYPA 612/613.

    Args:
        airport: Аэропорт — 'Larnaca' / 'LCA' или 'Paphos' / 'PFO'
        city: Опциональный город отправления/прибытия (например, 'Limassol', 'Nicosia', 'Paphos')
    """
    log.info(f"Tool called: get_airport_transfers(airport='{airport}', city='{city}')")
    airport_lower = airport.lower().strip()
    is_lca = "lar" in airport_lower or "lca" in airport_lower
    is_pfo = "paf" in airport_lower or "paph" in airport_lower or "pfo" in airport_lower

    if not is_lca and not is_pfo:
        return "❌ Укажите аэропорт: 'Larnaca' (LCA) или 'Paphos' (PFO)."

    results = []
    target_airport_name = "Larnaca Airport (LCA)" if is_lca else "Paphos Airport (PFO)"

    # Filter airport routes
    airport_routes = ["osypa_airport", "osypa_airport_613", "kapnos", "limassol_airport"]
    for r_key in airport_routes:
        if r_key not in ALL_ROUTES:
            continue
        info = ALL_ROUTES[r_key]

        # Check city filter
        if city:
            c_norm = _normalize_city_token(city)
            c_syns = CITY_SYNONYMS.get(c_norm, [c_norm])
            name_desc = f"{info['name']} {r_key}".lower()
            if not any(s in name_desc for s in c_syns):
                if r_key in ("osypa_airport", "osypa_airport_613") and "paphos" not in c_syns:
                    continue
                if r_key == "limassol_airport" and "limassol" not in c_syns and "paphos" not in c_syns and "larnaca" not in c_syns:
                    continue

        data = await _fetch_schedule(r_key)
        for direction in data:
            desc = direction.get("desc", "")
            times = direction.get("times", [])
            t_samples = [t.get("t") for t in times if t.get("t") != "LINK"]

            entry = [f"✈️ {direction.get('desc', info['name'])} ({info['name']})"]
            if direction.get("duration"):
                entry.append(f"   ⏱ В пути: {direction['duration']}")
            if direction.get("price"):
                entry.append(f"   💶 Цена: {direction['price']}")

            if t_samples:
                entry.append(f"   ⏰ Расписание: {', '.join(t_samples[:10])}")
                if len(t_samples) > 10:
                    entry.append(f"      (всего {len(t_samples)} рейсов)")
            else:
                entry.append(f"   🔗 Билеты и расписание онлайн: {info['url']}")

            results.append("\n".join(entry))

    if not results:
        return f"❌ Рейсов для аэропорта {target_airport_name} не найдено."

    header = f"✈️ Трансферы в/из {target_airport_name}:\n\n"
    return header + "\n\n".join(results)


@mcp.tool()
async def search_schedule(query: str) -> str:
    """
    Полнотекстовый поиск по расписанию автобусов Кипра (по названию остановки, достопримечательности или направления).
    Например: 'Coral Bay', 'Waterpark', 'Karavella', 'Petra Tou Romiou', 'Market'.

    Args:
        query: Поисковый запрос (например, 'Coral Bay', 'Аэропорт', 'Market')
    """
    log.info(f"Tool called: search_schedule(query='{query}')")
    q_lower = query.lower().strip()
    if not q_lower:
        return "❌ Введите поисковый запрос."

    matches = []
    for r_key, info in ALL_ROUTES.items():
        data = await _fetch_schedule(r_key)
        for direction in data:
            desc = direction.get("desc", "")
            name = direction.get("name", "")
            combined = f"{name} {desc}".lower()

            if q_lower in combined or q_lower in r_key.lower():
                times = [t.get("t") for t in direction.get("times", []) if t.get("t") != "LINK"]
                entry = [f"🚌 {desc} ({name})"]
                if direction.get("duration"):
                    entry.append(f"   ⏱ В пути: {direction['duration']}")
                if direction.get("price"):
                    entry.append(f"   💶 Цена: {direction['price']}")
                if times:
                    entry.append(f"   ⏰ Рейсы: {', '.join(times[:8])}")
                matches.append("\n".join(entry))

    if not matches:
        return f"❌ По запросу '{query}' рейсов не найдено."

    header = f"🔍 Результаты поиска по запросу '{query}':\n\n"
    return header + "\n\n".join(matches[:10])



# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 50)
    log.info("MCP CyBuses Intercity Server starting...")
    log.info(f"Transport: sse")
    log.info(f"Endpoint:  http://0.0.0.0:8999/sse")
    log.info(f"Routes:    {', '.join(ALL_ROUTES.keys())}")
    log.info("=" * 50)
    log.info("=" * 50)
    log.info("⚠️  This is NOT a web page! Do NOT open in browser.")
    log.info("    Connect via MCP client (Python SDK / Claude Desktop)")
    log.info("=" * 50)
    
    # В mcp SDK аргументы host/port передаются в конструктор FastMCP
    mcp.run(transport="sse")
