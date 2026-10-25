import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiohttp
from services.scraper import ScraperService
from config import ROUTES


sys.stdout.reconfigure(encoding='utf-8')

async def test_all_routes():
    scraper = ScraperService(concurrency_limit=3)
    async with aiohttp.ClientSession() as session:
        success_count = 0
        error_count = 0
        total_directions = 0
        total_departures = 0

        for key, info in ROUTES.items():
            prov = info.get("provider", "").upper()
            print(f"\n[{prov}] Fetching '{key}': {info['name']}")
            print(f"       URL: {info['url']}")
            try:
                res = await scraper.fetch_route(session, key, info)
                if not res:
                    print("       ❌ EMPTY RESULT")
                    error_count += 1
                elif res[0].get("hasError"):
                    print(f"       ❌ ERROR: {res[0].get('errorMsg')}")
                    error_count += 1
                else:
                    success_count += 1
                    total_directions += len(res)
                    route_deps = sum(len(d.get("times", [])) for d in res)
                    total_departures += route_deps
                    print(f"       ✅ SUCCESS: {len(res)} directions, {route_deps} departures.")
                    for d in res[:2]:
                        sample = [t['t'] for t in d['times'][:4]]
                        print(f"          - [{d['type']}] {d['desc']}: {len(d['times'])} times {sample}")
            except Exception as e:
                print(f"       💥 EXCEPTION: {e}")
                error_count += 1

        print(f"\n==========================================")
        print(f"FINAL RESULT:")
        print(f"  Successful routes: {success_count}/{len(ROUTES)}")
        print(f"  Failing routes:    {error_count}/{len(ROUTES)}")
        print(f"  Total directions:  {total_directions}")
        print(f"  Total departures:  {total_departures}")
        print(f"==========================================")

    await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_all_routes())
