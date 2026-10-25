import asyncio
import aiohttp
from services.scraper import ScraperService
from config import ROUTES

async def main():
    scraper = ScraperService()
    async with aiohttp.ClientSession() as session:
        for key, info in ROUTES.items():
            if info.get('provider') == 'osypa':
                print(f"Testing {key}...")
                res = await scraper.fetch_route(session, key, info)
                if not res or res[0].get('hasError'):
                    print(f"Error parsing {key}: {res}")
                else:
                    print(f"Success {key}: {len(res)} directions. Example data: {[t['t'] for t in res[0]['times']]}")

if __name__ == "__main__":
    asyncio.run(main())
