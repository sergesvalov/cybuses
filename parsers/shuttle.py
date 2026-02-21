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
        raw_results = []
        
        WEEKDAY_MARKERS = ["δευτέρα", "παρασκευή", "monday", "friday", "mon-fri", "mon", "fri"]
        WEEKEND_MARKERS = ["σάββατο", "κυριακή", "saturday", "sunday", "sat-sun", "sat & sun", "sat", "sun"]
        LIM_MARKERS = ["από λεμεσό", "απο λεμεσο", "from limassol", "αναχωρησεις απο λεμεσο", "αναχωρήσεις από λεμεσό", "limassol departures"]
        AIR_MARKERS = ["από αεροδρόμιο", "απο αεροδρομιο", "from airport", "from paphos", "from larnaca", "αναχωρησεις απο αεροδρομιο", "αναχωρήσεις από αεροδρόμιο", "airport departures", "από αεροδρόμιο πάφου", "από αεροδρόμιο λάρνακας", "from paphos airport", "from larnaca airport"]
        
        schedule = {
            "weekday": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []},
            "weekend": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []}
        }

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            current_day_type = "weekday"
            col_dirs = {"left": "Limassol ➝ Airport", "right": "Airport ➝ Limassol"}
                
            for page in pdf.pages:
                page_mid = page.width / 2
                words = page.extract_words()
                
                # Group words into lines
                words.sort(key=lambda w: (w['top'], w['x0']))
                
                lines = []
                for w in words:
                    added = False
                    if lines:
                        last_line = lines[-1]
                        if abs(last_line['top'] - w['top']) <= 5:
                            last_line['words'].append(w)
                            last_line['text'] += " " + w['text']
                            added = True
                    if not added:
                        lines.append({
                            'top': w['top'],
                            'words': [w],
                            'text': w['text']
                        })

                for line in lines:
                    low_text = line['text'].lower()

                    # 1. Detect Day Type
                    if any(m in low_text for m in WEEKEND_MARKERS):
                        current_day_type = "weekend"
                    elif any(m in low_text for m in WEEKDAY_MARKERS):
                        current_day_type = "weekday"

                    # 2. Split words into left and right halves
                    left_words = [w for w in line['words'] if w['x0'] < page_mid]
                    right_words = [w for w in line['words'] if w['x0'] >= page_mid]
                    
                    left_txt = " ".join([w['text'] for w in left_words]).lower()
                    right_txt = " ".join([w['text'] for w in right_words]).lower()

                    # 3. Detect column direction headers
                    if any(m in left_txt for m in LIM_MARKERS):
                        col_dirs["left"] = "Limassol ➝ Airport"
                    elif any(m in left_txt for m in AIR_MARKERS):
                        col_dirs["left"] = "Airport ➝ Limassol"
                        
                    if any(m in right_txt for m in LIM_MARKERS):
                        col_dirs["right"] = "Limassol ➝ Airport"
                    elif any(m in right_txt for m in AIR_MARKERS):
                        col_dirs["right"] = "Airport ➝ Limassol"

                    # 4. Extract times and push to corresponding column
                    for t_str, stars in self.extract_times(left_txt):
                        nt = self.normalize_time(t_str)
                        if ":" in nt:
                            h, m = map(int, nt.split(':'))
                            if 0 <= h <= 23 and 0 <= m <= 59:
                                d = col_dirs["left"]
                                if not any(x['t'] == nt for x in schedule[current_day_type][d]):
                                    schedule[current_day_type][d].append({
                                        "t": nt, "n": stars, "f": nt + stars, "note_txt": ""
                                    })
                                    
                    for t_str, stars in self.extract_times(right_txt):
                        nt = self.normalize_time(t_str)
                        if ":" in nt:
                            h, m = map(int, nt.split(':'))
                            if 0 <= h <= 23 and 0 <= m <= 59:
                                d = col_dirs["right"]
                                if not any(x['t'] == nt for x in schedule[current_day_type][d]):
                                    schedule[current_day_type][d].append({
                                        "t": nt, "n": stars, "f": nt + stars, "note_txt": ""
                                    })

        # Format output
        for d_type in ["weekday", "weekend"]:
            for direct, t_list in schedule[d_type].items():
                if t_list:
                    t_list.sort(key=lambda x: x['t'])
                    raw_results.append({
                        "name": info['name'],
                        "desc": direct,
                        "type": d_type,
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