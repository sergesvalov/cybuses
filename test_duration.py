import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def test():
    urls = [
        'https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/',
        'https://intercity-buses.com/en/routes/nicosia-paphos-paphos-nicosia/'
    ]
    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                duration_text = None
                for txt in soup.stripped_strings:
                    lower_txt = txt.lower()
                    if 'hour' in lower_txt and 'minute' in lower_txt and ('approximately' in lower_txt or 'duration' in lower_txt):
                        duration_text = txt
                        break
                print(f'{url}: {duration_text}')

asyncio.run(test())
