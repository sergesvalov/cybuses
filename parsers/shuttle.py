import io
import re
import aiohttp
import pdfplumber
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        """
        Продвинутый парсер для Kapnos:
        1. Заходит на сайт.
        2. Ищет ссылку на PDF.
        3. Скачивает PDF и парсит времена.
        """
        results = []
        base_url = info['url'] # https://kapnosairportshuttle.com/
        
        print(f"[SHUTTLE] Searching PDF on {base_url}...")
        
        # 1. Получаем HTML главной страницы, чтобы найти ссылку на PDF
        try:
            async with session.get(base_url, headers=self.HEADERS, ssl=False, timeout=15) as r:
                if r.status != 200:
                    return self.fallback_link(info, "Сайт недоступен")
                html = await r.text()
        except Exception as e:
            return self.fallback_link(info, f"Error: {e}")

        # 2. Ищем ссылку на PDF (обычно href заканчивается на .pdf)
        soup = BeautifulSoup(html, 'html.parser')
        pdf_link = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Ищем что-то похожее на файл расписания
            if '.pdf' in href.lower() or 'timetable' in href.lower():
                pdf_link = urljoin(base_url, href)
                # Если нашли явный PDF, берем его и выходим
                if '.pdf' in pdf_link.lower():
                    break
        
        if not pdf_link:
            return self.fallback_link(info, "PDF не найден")

        print(f"[SHUTTLE] Found PDF: {pdf_link}")

        # 3. Скачиваем PDF в память
        try:
            async with session.get(pdf_link, headers=self.HEADERS, ssl=False, timeout=30) as r:
                if r.status != 200:
                    return self.fallback_link(info, "Ошибка загрузки PDF")
                pdf_bytes = await r.read()
        except Exception as e:
            return self.fallback_link(info, f"Download err: {e}")

        # 4. Парсим PDF через pdfplumber
        try:
            extracted_data = self.extract_from_pdf(pdf_bytes)
        except Exception as e:
            print(f"PDF Parse Error: {e}")
            return self.fallback_link(info, "Ошибка чтения PDF")

        if not extracted_data:
            return self.fallback_link(info, "Данные в PDF не найдены")

        # 5. Формируем результаты
        for route_name, times in extracted_data.items():
            if not times: continue
            
            # Сортируем времена
            times.sort(key=lambda x: x['t'])
            
            # Добавляем ссылку на PDF, чтобы пользователь мог проверить
            results.append({
                "name": info['name'],
                "desc": route_name, # Например "FROM NICOSIA"
                "type": "all",
                "times": times,
                "url": pdf_link,    # Ссылка ведет прямо на PDF
                "prov": info['provider'],
                "notes": {}
            })

        return results

    def fallback_link(self, info, reason):
        """Возвращает просто кнопку-ссылку, если парсинг не удался"""
        return [{
            "name": info['name'], 
            "desc": f"Link Only ({reason})", 
            "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": "Открыть PDF ↗", "url": info['url']}], 
            "url": info['url'], 
            "prov": info['provider'], 
            "notes": {}
        }]

    def extract_from_pdf(self, pdf_bytes):
        """
        Логика вытаскивания текста из PDF байтов.
        Группирует времена по заголовкам (городам).
        """
        data = {}
        current_header = "General Schedule"
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                # Извлекаем текст, сохраняя примерную структуру
                text = page.extract_text()
                if not text: continue
                
                lines = text.split('\n')
                for line in lines:
                    line_clean = line.strip()
                    if not line_clean: continue
                    lower = line_clean.lower()
                    
                    # --- Поиск заголовков ---
                    # Kapnos обычно пишет "FROM NICOSIA", "LARNACA AIRPORT TO..."
                    is_header = any(x in lower for x in ["from ", " to ", "route", "nicosia", "larnaca", "paphos"])
                    has_digits = any(c.isdigit() for c in line_clean)
                    
                    # Если строка похожа на заголовок (есть города, мало цифр)
                    if is_header and len(line_clean) < 60 and not re.search(r'\d{1,2}[:.]\d{2}', line_clean):
                        current_header = line_clean.replace(":", "").title() # Делаем красиво "From Nicosia"
                        if current_header not in data:
                            data[current_header] = []
                        continue

                    # --- Поиск времен ---
                    raw = self.extract_times(line_clean)
                    if raw:
                        if current_header not in data:
                            data[current_header] = []
                            
                        for t, stars in raw:
                            nt = self.normalize_time(t)
                            # Фильтруем явный мусор
                            if "00:00" <= nt <= "23:59":
                                # Проверяем на дубли
                                if not any(x['t'] == nt for x in data[current_header]):
                                    data[current_header].append({
                                        "t": nt,
                                        "n": stars,
                                        "f": nt + stars
                                    })
        return data