import asyncio
import aiohttp
import time
from config import ROUTES
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

PARSER_MAP = {
    "intercity": IntercityParser(),
    "osypa": OsypaParser(),
    "shuttle": ShuttleParser()
}

async def fetch_route(session, key, info):
    provider_key = info.get('provider')
    parser = PARSER_MAP.get(provider_key)
    
    if not parser:
        return []

    print(f"[{provider_key.upper()}] Fetching: {info['name']}...")
    try:
        return await parser.parse(session, info)
    except Exception as e:
        print(f"!!! Error in {key}: {e}")
        return []

async def get_all_data_async():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for key, info in ROUTES.items():
            task = asyncio.create_task(fetch_route(session, key, info))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    
    flat_data = [item for sublist in results for item in sublist]
    print(f">>> Update finished in {time.time() - start_time:.2f} s.")
    return flat_data