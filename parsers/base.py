import re
import aiohttp
import asyncio
from curl_cffi import requests
from bs4 import BeautifulSoup

class BaseParser:
    def __init__(self):
        # Using curl_cffi to impersonate Chrome 120 and bypass Cloudflare 403s
        self.session = requests.AsyncSession(impersonate="chrome120")
    
    TIME_REGEX = re.compile(r'\b((?:[01]?\d|2[0-3]):[0-5]\d)([\*]*)')

    async def get_soup(self, session: aiohttp.ClientSession, url: str):
        # We ignore aiohttp session here because it gets blocked by Cloudflare.
        # Instead, we use curl_cffi.requests.AsyncSession.
        try:
            response = await self.session.get(url, timeout=25)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"HTTP ERROR {response.status_code} for {url}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def normalize_time(self, t_str):
        t_str = t_str.replace('.', ':').strip()
        if len(t_str) == 4 and ':' in t_str: return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        return self.TIME_REGEX.findall(text)