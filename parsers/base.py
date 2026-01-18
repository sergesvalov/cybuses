import re
import aiohttp
from bs4 import BeautifulSoup

class BaseParser:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    async def get_soup(self, session: aiohttp.ClientSession, url: str):
        try:
            async with session.get(url, headers=self.HEADERS, timeout=25, ssl=False) as response:
                if response.status == 200:
                    text = await response.text()
                    return BeautifulSoup(text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def normalize_time(self, t_str):
        t_str = t_str.replace('.', ':').strip()
        if len(t_str) == 4 and ':' in t_str: return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        return re.findall(r'(\d{1,2}[:.]\d{2})([\*]*)', text)