import asyncio
import aiohttp
import time
from config import ROUTES

# Import parsers
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

# Parser Registry
PARSER_MAP = {
    "intercity": IntercityParser(),
    "osypa": OsypaParser(),
    "shuttle": ShuttleParser()
}

async def fetch_route(session, key, info):
    """
    Fetches data for a single route using the appropriate parser.
    """
    provider_key = info.get('provider')
    parser = PARSER_MAP.get(provider_key)
    
    if not parser:
        print(f"Unknown provider for {key}")
        return []

    print(f"[{provider_key.upper()}] Fetching: {info['name']}...")
    try:
        # Calls the async parse method
        return await parser.parse(session, info)
    except Exception as e:
        print(f"!!! Error in {key}: {e}")
        return []

async def get_all_data_async():
    """
    Main entry point for scraping.
    Runs all route fetchers in parallel.
    """
    start_time = time.time()
    
    # Create a single session for all requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        for key, info in ROUTES.items():
            # Schedule the task
            task = asyncio.create_task(fetch_route(session, key, info))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
    
    # Flatten the list of lists
    flat_data = [item for sublist in results for item in sublist]
    
    duration = time.time() - start_time
    print(f">>> Update finished in {duration:.2f} seconds.")
    return flat_data