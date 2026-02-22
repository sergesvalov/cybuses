import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def main():
    url = 'https://intercity-buses.com/en/routes/paphos-ayia-napa-paralimni-paphos/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, ssl=False) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')
    print('--- RAW ASTERISKS TEXT IN HTML ---')
    for tag in soup.find_all(['p', 'div', 'span', 'li', 'td', 'strong', 'em', 'b', 'i']):
        txt = tag.get_text(' ', strip=True)
        if txt.startswith('*'):
            print(repr(txt))
            match = re.match(r'^(\*+)\s+(.+)', txt)
            match_ns = re.match(r'^(\*+)\s*(.+)', txt)
            print(f'Match with space: {bool(match)}, without space: {bool(match_ns)}')

asyncio.run(main())
