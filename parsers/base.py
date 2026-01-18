import re
import aiohttp
from bs4 import BeautifulSoup

class BaseParser:
    """
    Base class for all parsers.
    Handles async HTTP requests and time normalization.
    """
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    async def get_soup(self, session: aiohttp.ClientSession, url: str):
        """
        Fetches the HTML content asynchronously and returns a BeautifulSoup object.
        """
        try:
            # ssl=False is equivalent to verify=False in requests
            async with session.get(url, headers=self.HEADERS, timeout=25, ssl=False) as response:
                if response.status == 200:
                    text = await response.text()
                    return BeautifulSoup(text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def normalize_time(self, t_str):
        """Converts time strings like '9.30' to '09:30'."""
        t_str = t_str.replace('.', ':').strip()
        # Add leading zero if needed (e.g., 9:30 -> 09:30)
        if len(t_str) == 4 and ':' in t_str: 
            return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        """Finds time patterns like 12:30 or 12.30 in text."""
        return re.findall(r'(\d{1,2}[:.]\d{2})([\*]*)', text)

    def extract_notes(self, soup):
        """
        Extracts notes/legends if present on the page.
        (Placeholder logic based on previous sync implementation)
        """
        notes = {}
        # Add logic here if specific parsers need to extract footnotes
        return notes