import re
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaseParser:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    def get_soup(self, url):
        """Общая функция для получения HTML"""
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=25, verify=False)
            if r.status_code == 200:
                return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def normalize_time(self, t_str):
        """Приводит время к формату 09:30"""
        t_str = t_str.replace('.', ':').strip()
        if len(t_str) == 4 and ':' in t_str: return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        """Ищет 12:30 или 12.30"""
        return re.findall(r'(\d{1,2}[:.]\d{2})([\*]*)', text)

    def extract_notes(self, soup):
        """Собирает сноски (*)"""
        notes = {}
        if not soup: return notes
        for el in soup.find_all(['p', 'span', 'li', 'td', 'div']):
            txt = el.get_text(strip=True)
            m = re.match(r'^([\*]+)\s*(.+)', txt)
            if m: notes[m.group(1)] = m.group(2)
        return notes
    
    def parse(self, info):
        """Этот метод должен быть переопределен в дочерних классах"""
        raise NotImplementedError