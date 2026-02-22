import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_prices():
    url = 'https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')
    print("--- Searching for Euro symbols ---")
    
    # Prices are usually in tables or paragraphs with Euro sign
    tags = soup.find_all(string=lambda t: t and '€' in t)
    for tag in tags:
        parent = tag.parent
        if parent:
            text = parent.get_text(strip=True)
            print(f"Tag <{parent.name}>: {text}")

asyncio.run(fetch_prices())
