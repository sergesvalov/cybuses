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
