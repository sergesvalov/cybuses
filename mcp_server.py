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
from datetime import datetime, timedelta
from typing import Optional

# Задаем переменные окружения ДО импорта и создания FastMCP
os.environ["FASTMCP_HOST"] = "0.0.0.0"
os.environ["FASTMCP_PORT"] = "8999"

from mcp.server.fastmcp import FastMCP

# --- Reuse project internals ---
from config import ROUTES
from parsers.intercity import IntercityParser

# ── Logging setup ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("mcp-cybuses")

# Добавляем подробное логирование для внутренних веб-компонентов
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
logging.getLogger("starlette").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)

# ── Server setup ────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="CyBuses Intercity",
    host="0.0.0.0",
    port=8999,
    instructions=(
        "This MCP server provides real-time intercity bus schedules for Cyprus. "
        "Routes: Paphos ↔ Limassol, Paphos ↔ Nicosia, Paphos ↔ Larnaca, Nicosia ↔ Limassol. "
        "Use get_intercity_routes to list routes, get_schedule to see full timetable, "
        "and get_nearest_bus to find the next departure."
    ),
    sse_path="/sse"  # Стандартный путь для SSE
)

# ── Simple in-memory cache (TTL = 5 min) ────────────────────────────────────

_cache: dict[str, dict] = {}          # route_key -> {"data": [...], "ts": datetime}
CACHE_TTL = timedelta(minutes=5)
_parser = IntercityParser()

INTERCITY_ROUTES = {k: v for k, v in ROUTES.items() if v.get("provider") == "intercity"}


async def _fetch_schedule(route_key: str) -> list[dict]:
    """Fetch schedule from website or return from cache."""
    now = datetime.now()

    if route_key in _cache:
        entry = _cache[route_key]
        age = now - entry["ts"]
        if age < CACHE_TTL:
            log.info(f"Cache HIT for '{route_key}' (age: {age.seconds}s)")
            return entry["data"]

    log.info(f"Cache MISS for '{route_key}', fetching from website...")
    info = INTERCITY_ROUTES[route_key]
    try:
        async with aiohttp.ClientSession() as session:
            data = await _parser.parse(session, info)
        log.info(f"Fetched '{route_key}': {len(data)} direction(s), "
                 f"{sum(len(d.get('times', [])) for d in data)} time entries")
    except Exception as e:
        log.error(f"Failed to fetch '{route_key}': {e}")
        return []

    _cache[route_key] = {"data": data, "ts": now}
    return data


def _format_schedule_text(data: list[dict]) -> str:
    """Format parsed schedule data into a human-readable string."""
    if not data:
        return "Расписание не найдено. Попробуйте позже."

    lines = []
    for direction in data:
        lines.append(f"🚌 {direction['desc']}")
        if direction.get("price"):
            lines.append(f"   💶 Цена: {direction['price']}")

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
async def get_intercity_routes() -> str:
    """
    Возвращает список доступных междугородних маршрутов автобусов (Intercity).
    Используй этот инструмент чтобы узнать какие маршруты доступны.
    """
    log.info("Tool called: get_intercity_routes")
    lines = ["📋 Доступные маршруты Intercity:", ""]
    for key, info in INTERCITY_ROUTES.items():
        lines.append(f"• {info['name']} — route_key: \"{key}\"")
        lines.append(f"  URL: {info['url']}")
    lines.append("")
    lines.append("Используй get_schedule(route) или get_nearest_bus(route) для подробностей.")
    return "\n".join(lines)


@mcp.tool()
async def get_schedule(route: str) -> str:
    """
    Возвращает полное расписание автобусов для указанного маршрута.
    Включает оба направления, времена отправления, цены и примечания.

    Args:
        route: Ключ маршрута — "limassol", "nicosia", "larnaca" или "nicosia_limassol"
    """
    log.info(f"Tool called: get_schedule(route='{route}')")
    route = route.lower().strip()
    if route not in INTERCITY_ROUTES:
        available = ", ".join(INTERCITY_ROUTES.keys())
        log.warning(f"Unknown route '{route}', available: {available}")
        return f"❌ Неизвестный маршрут '{route}'. Доступные: {available}"

    data = await _fetch_schedule(route)
    header = f"📅 Расписание: {INTERCITY_ROUTES[route]['name']}\n"
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
        route: Ключ маршрута — "limassol", "nicosia", "larnaca" или "nicosia_limassol"
        direction: Направление — "dir1" или "dir2". 
                   Если не указано, показывает ближайшие для обоих направлений.
    """
    log.info(f"Tool called: get_nearest_bus(route='{route}', direction='{direction}')")
    route = route.lower().strip()
    if route not in INTERCITY_ROUTES:
        available = ", ".join(INTERCITY_ROUTES.keys())
        log.warning(f"Unknown route '{route}', available: {available}")
        return f"❌ Неизвестный маршрут '{route}'. Доступные: {available}"

    data = await _fetch_schedule(route)
    if not data:
        return "❌ Не удалось загрузить расписание."

    now = datetime.now()
    now_str = now.strftime("%H:%M")
    results = []

    for dir_data in data:
        desc = dir_data["desc"]

        # Filter by direction if specified
        if direction:
            direction = direction.lower().strip()
            city1_name = INTERCITY_ROUTES[route]['city1'].title()
            city2_name = INTERCITY_ROUTES[route]['city2'].title()
            
            if direction == "dir1" and "➝" in desc and desc.startswith(city1_name):
                pass  # match
            elif direction == "dir2" and "➝" in desc and desc.startswith(city2_name):
                pass  # match
            else:
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

            log.info(f"Next bus {desc}: {next_bus['t']} (in {minutes_left} min)")
            results.append(
                f"🚌 {desc}\n"
                f"   ⏰ Ближайший: {next_bus['t']}{note}\n"
                f"   ⏳ Через {minutes_left} мин"
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

    header = f"🕐 Ближайшие автобусы ({now.strftime('%H:%M')}) — {INTERCITY_ROUTES[route]['name']}\n\n"
    result_text = header + "\n".join(results).strip()
    snippet = result_text[:100].replace('\n', ' ')
    log.info(f"get_nearest_bus returning {len(result_text)} chars. Snippet: {snippet}...")
    return result_text


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 50)
    log.info("MCP CyBuses Intercity Server starting...")
    log.info(f"Transport: sse")
    log.info(f"Endpoint:  http://0.0.0.0:8999/sse")
    log.info(f"Routes:    {', '.join(INTERCITY_ROUTES.keys())}")
    log.info(f"Cache TTL: {CACHE_TTL}")
    log.info("=" * 50)
    log.info("⚠️  This is NOT a web page! Do NOT open in browser.")
    log.info("    Connect via MCP client (Python SDK / Claude Desktop)")
    log.info("=" * 50)
    
    # В mcp SDK аргументы host/port передаются в конструктор FastMCP
    mcp.run(transport="sse")
