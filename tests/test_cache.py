import pytest
import asyncio
from services.cache import CacheManager


@pytest.mark.anyio
async def test_cache_manager_state():
    cm = CacheManager()
    assert cm.is_updating() is False
    
    cm.set_updating(True)
    assert cm.is_updating() is True
    
    cm.set_updating(False)
    assert cm.is_updating() is False


@pytest.mark.anyio
async def test_cache_manager_in_memory_cache():
    cm = CacheManager()
    mock_data = [
        {
            "prov": "intercity",
            "name": "Paphos ↔ Limassol",
            "desc": "Paphos ➝ Limassol",
            "type": "weekday",
            "url": "https://example.com",
            "times": [{"t": "08:00", "n": "", "f": "08:00", "note_txt": ""}],
            "notes": {}
        }
    ]
    # Set mock memory cache directly
    cm._cached_data = mock_data
    
    # get_data should return memory cache without querying DB
    data = await cm.get_data()
    assert len(data) == 1
    assert data[0]["name"] == "Paphos ↔ Limassol"
    assert data[0]["times"][0]["t"] == "08:00"

    # Invalidation should clear it
    cm.invalidate_memory_cache()
    assert cm._cached_data is None
