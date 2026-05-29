import json
import os
import asyncio

CACHE_FILE = "bus_cache.json"

class CacheManager:
    def __init__(self):
        self._memory_cache = []
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
        """Reads the cache file from disk and saves it to memory."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f: 
                    self._memory_cache = json.load(f)
                print(f">>> Cache loaded from disk: {len(self._memory_cache)} routes")
            except Exception as e:
                print(f"Error loading cache from disk: {e}")
                self._memory_cache = []
        else:
            print(">>> No cache file found on disk.")

    def update_cache(self, data, has_errors=False):
        """Updates the memory and disk caches with new data."""
        if not data:
            print(">>> Update returned empty data. Keeping old cache.")
            return

        if has_errors and self._memory_cache:
            print(">>> Parsers encountered errors. Merging successful results with old cache.")
            # Map old cache by unique key to preserve it
            old_routes = {(r['prov'], r['name'], r['desc']): r for r in self._memory_cache}
            
            # Override with successful new pulls
            for new_r in data:
                old_routes[(new_r['prov'], new_r['name'], new_r['desc'])] = new_r
                
            merged_data = list(old_routes.values())
            self._memory_cache = merged_data
            data_to_save = merged_data
        else:
            self._memory_cache = data
            data_to_save = data
            
        try:
            tmp = CACHE_FILE + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f: 
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CACHE_FILE)
            print(f">>> Cache Updated Successfully. Routes: {len(data_to_save)}")
        except Exception as e:
            print(f"Error saving cache to disk: {e}")

    def get_data(self):
        return self._memory_cache

    def set_updating(self, is_updating: bool):
        self._updating = is_updating
        event = self._get_event()
        if is_updating:
            event.clear()
        else:
            event.set()

    def is_updating(self):
        return self._updating
