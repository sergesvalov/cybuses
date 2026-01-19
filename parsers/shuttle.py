import io
import re
import pdfplumber
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        url = info['url']
        
        # Если это прямая ссылка на PDF (Лимассол)
        if url.lower().endswith('.pdf'):
            return await self.process_pdf(session, url, info)

        # Если это Kapnos (поиск на странице)
        elif "kapnos" in url:
            return await self.find_and_parse_kapnos(session, info)

        return self.fallback_link(info, "Unknown Provider")

    async def process_pdf(self, session, pdf_url, info):
        try:
            async with session.get(pdf_url, headers=self.HEADERS, ssl=False, timeout=30) as r:
                if r.status != 200: return self.fallback_link(info, "PDF Access Error")
                pdf_bytes = await r.read()
        except Exception as e: 
            return self.fallback_link(info, f"Download Error: {e}")

        try:
            # Вызываем улучшенный парсинг
            results = self.extract_limassol_express_logic(pdf_bytes, pdf_url, info)
            return results if results else self.fallback_link(info, "No data extracted")
        except Exception as e:
            print(f"PDF Error: {e}")
            return self.fallback_link(info, "Parse Error")

    def extract_limassol_express_logic(self, pdf_bytes, pdf_url, info):
        """
        Улучшенная логика специально для Limassol Express с учетом греческого языка
        и разделения по дням недели.
        """
        raw_results = []
        
        # Ключевые слова для определения типа дня
        WEEKDAY_MARKERS = ["Δευτέρα", "Παρασκευή", "Monday", "Friday", "Mon-Fri"]
        WEEKEND_MARKERS = ["Σάββατο", "Κυριακή", "Saturday", "Sunday", "Sat-Sun", "Sat & Sun"]

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                # Состояния для парсинга текущей страницы
                current_day_type = "weekday" 
                current_direction = "Limassol ➝ Airport"
                
                # Временные хранилища
                schedule = {
                    "weekday": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []},
                    "weekend": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []}
                }

                lines = text.split('\n')
                for line in lines:
                    clean = line.strip()
                    if not clean: continue
                    lower = clean.lower()

                    # 1. Определяем тип дня (Будни / Выходные)
                    if any(m in clean for m in WEEKEND_MARKERS):
                        current_day_type = "weekend"
                    elif any(m in clean for m in WEEKDAY_MARKERS):
                        current_day_type = "weekday"

                    # 2. Определяем направление
                    # Греческий: Λεμεσός (Лимассол), Αεροδρόμιο (Аэропорт)
                    if "από λεμεσό" in lower or "from limassol" in lower:
                        current_direction = "Limassol ➝ Airport"
                    elif "από αεροδρόμιο" in lower or "from airport" in lower:
                        current_direction = "Airport ➝ Limassol"

                    # 3. Извлекаем время
                    times = self.extract_times(clean)
                    for t_str, stars in times:
                        nt = self.normalize_time(t_str)
                        # Валидация: исключаем мусорные цифры (типа 2025 или части телефонов)
                        # Время должно быть в рамках 00:00 - 23:59
                        if ":" in nt:
                            h, m = map(int, nt.split(':'))
                            if 0 <= h <= 23 and 0 <= m <= 59:
                                # Проверка на дубликаты
                                if not any(x['t'] == nt for x in schedule[current_day_type][current_direction]):
                                    schedule[current_day_type][current_direction].append({
                                        "t": nt, "n": stars, "f": nt + stars, "note_txt": ""
                                    })

                # Превращаем накопленные данные в формат для фронтенда
                for d_type in ["weekday", "weekend"]:
                    for direct, t_list in schedule[d_type].items():
                        if t_list:
                            t_list.sort(key=lambda x: x['t'])
                            raw_results.append({
                                "name": info['name'],
                                "desc": direct,
                                "type": d_type, # Теперь корректно ставится weekday/weekend
                                "times": t_list,
                                "url": pdf_url,
                                "prov": info['provider'],
                                "notes": {}
                            })
        return raw_results

    async def find_and_parse_kapnos(self, session, info):
        # Логика для Капноса остается аналогичной, но использует 
        # тот же улучшенный метод валидации времени
        base_url = info['url']
        try:
            async with session.get(base_url, headers=self.HEADERS, ssl=False, timeout=15) as r:
                html = await r.text()
            soup = BeautifulSoup(html, 'html.parser')
            pdf_link = None
            for a in soup.find_all('a', href=True):
                if '.pdf' in a['href'].lower():
                    pdf_link = urljoin(base_url, a['href'])
                    break
            if pdf_link:
                return await self.process_pdf(session, pdf_link, info)
        except: pass
        return self.fallback_link(info, "PDF not found")

    def fallback_link(self, info, reason):
        return [{
            "name": info['name'], "desc": f"External Link ({reason})", "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": "Открыть расписание ↗", "url": info['url']}], 
            "url": info['url'], "prov": info['provider'], "notes": {}
        }]