import json
import os
import asyncio

CACHE_FILE = "bus_cache.json"

class CacheManager:
    def __init__(self):
        self._memory_cache = []
        self._updating = False

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

    def update_cache(self, data):
        """Updates the memory and disk caches with new data."""
        if not data:
            print(">>> Update returned empty data. Keeping old cache.")
            return

        self._memory_cache = data
        try:
            tmp = CACHE_FILE + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f: 
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CACHE_FILE)
            print(f">>> Cache Updated Successfully. Routes: {len(data)}")
        except Exception as e:
            print(f"Error saving cache to disk: {e}")

    def get_data(self):
        return self._memory_cache

    def set_updating(self, is_updating: bool):
        self._updating = is_updating

    def is_updating(self):
        return self._updating
