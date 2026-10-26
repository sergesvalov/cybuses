import pytest
from mcp_server import _format_schedule_text, get_routes, get_intercity_routes


def test_format_schedule_text_empty():
    assert _format_schedule_text([]) == "Расписание не найдено. Попробуйте позже."


def test_format_schedule_text_normal():
    sample_data = [
        {
            "desc": "Paphos ➝ Limassol",
            "price": "€4.00",
            "duration": "~ 1h 15m",
            "times": [
                {"t": "06:00", "n": "", "note_txt": ""},
                {"t": "07:30", "n": "*", "note_txt": "Term only"}
            ],
            "notes": {"*": "Runs only during school term"}
        }
    ]
    text = _format_schedule_text(sample_data)
    assert "Paphos ➝ Limassol" in text
    assert "€4.00" in text
    assert "06:00" in text
    assert "07:30 (Term only)" in text
    assert "* — Runs only during school term" in text


@pytest.mark.anyio
async def test_mcp_get_routes():
    routes_text = await get_routes()
    assert "limassol" in routes_text
    assert "nicosia" in routes_text

    # Test alias
    alias_text = await get_intercity_routes()
    assert alias_text == routes_text


@pytest.mark.anyio
async def test_mcp_find_bus(monkeypatch):
    from mcp_server import find_bus

    async def mock_fetch(route_key):
        if route_key == "limassol":
            return [
                {
                    "name": "Paphos ↔ Limassol",
                    "desc": "Limassol ➝ Paphos",
                    "price": "€4.00",
                    "duration": "~ 1h 15m",
                    "times": [
                        {"t": "08:00", "n": "", "note_txt": ""},
                        {"t": "14:00", "n": "", "note_txt": ""}
                    ]
                }
            ]
        return []

    monkeypatch.setattr("mcp_server._fetch_schedule", mock_fetch)
    res = await find_bus(origin="Лимассол", destination="Пафос", at_time="07:00")
    assert "Limassol ➝ Paphos" in res
    assert "08:00" in res

    # Not found case
    res_none = await find_bus(origin="Никосия", destination="Айя-Напа", at_time="07:00")
    assert "не найдено" in res_none


@pytest.mark.anyio
async def test_mcp_airport_transfers(monkeypatch):
    from mcp_server import get_airport_transfers

    async def mock_fetch(route_key):
        if route_key == "osypa_airport":
            return [
                {
                    "name": "612: Harbour - Airport",
                    "desc": "Harbour - Airport",
                    "times": [{"t": "09:00", "n": "", "note_txt": ""}]
                }
            ]
        return []

    monkeypatch.setattr("mcp_server._fetch_schedule", mock_fetch)
    res = await get_airport_transfers(airport="Paphos", city="Paphos")
    assert "Harbour - Airport" in res
    assert "09:00" in res


@pytest.mark.anyio
async def test_mcp_search_schedule(monkeypatch):
    from mcp_server import search_schedule

    async def mock_fetch(route_key):
        if route_key == "osypa_615":
            return [
                {
                    "name": "615: Harbour - Coral Bay",
                    "desc": "Harbour - Coral Bay",
                    "times": [{"t": "10:00", "n": "", "note_txt": ""}]
                }
            ]
        return []

    monkeypatch.setattr("mcp_server._fetch_schedule", mock_fetch)
    res = await search_schedule(query="Coral Bay")
    assert "Coral Bay" in res
    assert "10:00" in res

