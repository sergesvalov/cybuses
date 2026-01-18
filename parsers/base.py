import re
import requests
import urllib3
from bs4 import BeautifulSoup

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaseParser:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    def get_soup(self, url):
        """Скачивает страницу и возвращает объект BeautifulSoup"""
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=30, verify=False)
            if r.status_code == 200:
                # Используем lxml для скорости, если есть, иначе html.parser
                return BeautifulSoup(r.text, 'html.parser')
            print(f"Ошибка запроса {url}: Status {r.status_code}")
        except Exception as e:
            print(f"Исключение при запросе {url}: {e}")
        return None

    def normalize_time(self, t_str):
        """Форматирует 9.30 -> 09:30"""
        if not t_str: return ""
        t_str = t_str.replace('.', ':').strip()
        if len(t_str) == 4 and ':' in t_str: return f"0{t_str}" 
        return t_str

    def extract_times(self, text):
        """Находит все времена в тексте"""
        if not text: return []
        return re.findall(r'(\d{1,2}[:.]\d{2})', text)

    def extract_notes(self, soup):
        """Ищет сноски со звездочками"""
        notes = {}
        if not soup: return notes
        for el in soup.find_all(['p', 'span', 'div', 'li']):
            txt = el.get_text(strip=True)
            m = re.match(r'^(\*+)\s*(.+)', txt)
            if m: notes[m.group(1)] = m.group(2)
        return notes
    
    def get_data(self):
        """
        ГЛАВНЫЙ МЕТОД.
        Именно его вызывает scraper.py.
        """
        raise NotImplementedError("Метод get_data должен быть переопределен в дочернем классе")