import re
import requests
import urllib3
from bs4 import BeautifulSoup

# Disable warnings for insecure HTTPS requests (common with legacy websites)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaseParser:
    """
    Base class providing utility methods for scraping.
    All specific parsers must inherit from this class.
    """
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    def get_soup(self, url):
        """
        Fetches the URL and returns a BeautifulSoup object.
        Includes timeout and SSL verification disabling.
        """
        try:
            # timeout=30 prevents the scraper from hanging indefinitely
            r = requests.get(url, headers=self.HEADERS, timeout=30, verify=False)
            if r.status_code == 200:
                # Using 'lxml' parser if available (faster), otherwise standard html.parser
                return BeautifulSoup(r.text, 'html.parser')
            print(f"Failed to fetch {url}: Status code {r.status_code}")
        except Exception as e:
            print(f"Exception while fetching {url}: {e}")
        return None

    def normalize_time(self, t_str):
        """
        Normalizes time string format (e.g., '9.30' -> '09:30').
        """
        if not t_str: return ""
        t_str = t_str.replace('.', ':').strip()
        # Add leading zero if needed (e.g., 9:30 -> 09:30)
        if len(t_str) == 4 and ':' in t_str: return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        """
        Finds all time patterns (HH:MM or HH.MM) in a text string.
        Returns a list of strings.
        """
        if not text: return []
        return re.findall(r'(\d{1,2}[:.]\d{2})', text)

    def extract_notes(self, soup):
        """
        Extracts footnotes marked with asterisks (*).
        """
        notes = {}
        if not soup: return notes
        # Look for typical elements that might contain footnotes
        for el in soup.find_all(['p', 'span', 'div', 'li']):
            txt = el.get_text(strip=True)
            # Regex matches "* Some text" or "** Some text"
            m = re.match(r'^(\*+)\s*(.+)', txt)
            if m: notes[m.group(1)] = m.group(2)
        return notes
    
    def get_data(self):
        """
        MAIN ENTRY POINT.
        This method must be overridden by child classes.
        """
        raise NotImplementedError("The get_data() method must be implemented by the subclass")