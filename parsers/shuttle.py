import io
import re
import pdfplumber
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        url = info['url']
        
        # 1. Если это прямая ссылка на PDF (как у Лимассола)
        if url.lower().endswith('.pdf'):
            print(f"[SHUTTLE] Direct PDF download: {info['name']}...")
            return await self.process_pdf(session, url, info)

        # 2. Если это Kapnos (ищем PDF на странице)
        elif "kapnos" in url:
            print(f"[SHUTTLE] Searching PDF for {info['name']}...")
            return await self.find_and_parse_kapnos(session, info)

        # 3. Если это HTML страница Лимассола (старый вариант)
        elif "limassolairportexpress" in url:
            return await self.parse_limassol_html(session, info)

        return self.fallback_link(info, "Unknown Provider")

    # --- УНИВЕРСАЛЬНАЯ ФУНКЦИЯ СКАЧИВАНИЯ И ПАРСИНГА PDF ---
    async def process_pdf(self, session, pdf_url, info):
        try:
            async with session.get(pdf_url, headers=self.HEADERS, ssl=False, timeout=30) as r:
                if r.status != 200: return self.fallback_link(info, "PDF Error")
                pdf_bytes = await r.read()
        except Exception as e: 
            return self.fallback_link(info, f"Download Error: {e}")

        try:
            # Парсим байты
            data = self.extract_from_pdf(pdf_bytes)
            
            results = []
            for k, v in data.items():
                if v:
                    v.sort(key=lambda x: x['t'])
                    results.append({
                        "name": info['name'], "desc": k, "type": "all", "times": v,
                        "url": pdf_url, "prov": info['provider'], "notes": {}
                    })
            
            if not results:
                return self.fallback_link(info, "PDF формат не распознан")
            
            return results
        except Exception as e:
            print(f"PDF Parse Error: {e}")
            return self.fallback_link(info, "Ошибка чтения PDF")

    # --- ЛОГИКА ИЗВЛЕЧЕНИЯ ТЕКСТА (pdfplumber) ---
    def extract_from_pdf(self, pdf_bytes):
        data = {}
        current_header = "General Schedule"
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                # Читаем построчно
                for line in text.split('\n'):
                    clean = line.strip()
                    if not clean: continue
                    lower = clean.lower()
                    
                    # Ключевые слова для заголовков (Добавил limassol, havouzas)
                    keywords = ["from ", " to ", "nicosia", "larnaca", "paphos", "limassol", "havouzas", "airport"]
                    is_header_line = any(x in lower for x in keywords)
                    
                    # Эвристика заголовка: есть ключевые слова, нет времени, длина < 80
                    if is_header_line and len(clean) < 80 and not re.search(r'\d{1,2}[:.]\d{2}', clean):
                        # Красивое форматирование заголовка
                        current_header = clean.replace(":", "").title()
                        if "Havouzas" in current_header: current_header = "Limassol (Havouzas) ➝ Airport"
                        if "Paphos Airport" in current_header: current_header = "Airport ➝ Limassol"
                        
                        if current_header not in data: data[current_header] = []
                        continue
                    
                    # Поиск времени
                    raw = self.extract_times(clean)
                    if raw:
                        if current_header not in data: data[current_header] = []
                        for t, stars in raw:
                            nt = self.normalize_time(t)
                            if "00:00" <= nt <= "23:59":
                                # Проверка на дубликаты
                                if not any(x['t'] == nt for x in data[current_header]):
                                    data[current_header].append({"t": nt, "n": stars, "f": nt + stars})
        return data

    # --- ЛОГИКА ДЛЯ KAPNOS (Поиск ссылки) ---
    async def find_and_parse_kapnos(self, session, info):
        base_url = info['url']
        try:
            async with session.get(base_url, headers=self.HEADERS, ssl=False, timeout=15) as r:
                if r.status != 200: return self.fallback_link(info, "Site down")
                html = await r.text()
        except: return self.fallback_link(info, "Connection Error")

        soup = BeautifulSoup(html, 'html.parser')
        pdf_link = None
        for a in soup.find_all('a', href=True):
            if '.pdf' in a['href'].lower() or 'timetable' in a['href'].lower():
                pdf_link = urljoin(base_url, a['href'])
                if '.pdf' in pdf_link.lower(): break
        
        if not pdf_link: return self.fallback_link(info, "PDF not found on site")
        
        # Переиспользуем функцию скачивания
        return await self.process_pdf(session, pdf_link, info)

    # --- HTML (Legacy support) ---
    async def parse_limassol_html(self, session, info):
        # (Оставляем старую логику на всякий случай, если вернут HTML)
        # ... код такой же как был, но можно и удалить, если уверены в PDF ...
        # Для краткости возвращаю фолбек, т.к. мы перешли на PDF
        return self.fallback_link(info, "HTML mode deprecated")

    def fallback_link(self, info, reason):
        label = "Открыть PDF ↗"
        return [{
            "name": info['name'], "desc": f"External Link ({reason})", "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": label, "url": info['url']}], 
            "url": info['url'], "prov": info['provider'], "notes": {}
        }]