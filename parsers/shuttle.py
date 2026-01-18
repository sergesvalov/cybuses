import io
import re
import pdfplumber
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        url = info['url']
        if "limassolairportexpress" in url:
            return await self.parse_limassol_html(session, info)
        elif "kapnos" in url:
            return await self.parse_kapnos_pdf(session, info)
        return self.fallback_link(info, "Unknown Provider")

    async def parse_limassol_html(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return self.fallback_link(info, "Site Error")

        groups = {}
        current_head = "Schedule"
        elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'strong', 'td', 'li'])
        
        for el in elements:
            txt = el.get_text(" ", strip=True)
            if not txt: continue
            lower = txt.lower()
            is_lim = "limassol" in lower or "havouzas" in lower
            is_air = "airport" in lower
            
            if (is_lim or is_air) and len(txt) < 100 and not re.search(r'\d{1,2}[:.]\d{2}', txt):
                clean = txt.replace(":", "").strip()
                if "havouzas" in lower: current_head = "Limassol ➝ Airport"
                elif "airport" in lower: current_head = "Airport ➝ Limassol"
                else: current_head = clean
                if current_head not in groups: groups[current_head] = []
                continue

            raw = self.extract_times(txt)
            if raw:
                if current_head not in groups: groups[current_head] = []
                for t, stars in raw:
                    nt = self.normalize_time(t)
                    if "00:00" <= nt <= "23:59":
                        if not any(x['t'] == nt for x in groups[current_head]):
                            groups[current_head].append({"t": nt, "n": stars, "f": nt + stars})

        for head, t_list in groups.items():
            if t_list:
                t_list.sort(key=lambda x: x['t'])
                results.append({
                    "name": info['name'], "desc": head, "type": "all", "times": t_list,
                    "url": info['url'], "prov": "shuttle", "notes": {}
                })
        return results or self.fallback_link(info, "No data found")

    async def parse_kapnos_pdf(self, session, info):
        base_url = info['url']
        try:
            async with session.get(base_url, headers=self.HEADERS, ssl=False, timeout=15) as r:
                if r.status != 200: return self.fallback_link(info, "Site down")
                html = await r.text()
        except Exception as e: return self.fallback_link(info, str(e))

        soup = BeautifulSoup(html, 'html.parser')
        pdf_link = None
        for a in soup.find_all('a', href=True):
            if '.pdf' in a['href'].lower() or 'timetable' in a['href'].lower():
                pdf_link = urljoin(base_url, a['href'])
                if '.pdf' in pdf_link.lower(): break
        
        if not pdf_link: return self.fallback_link(info, "PDF not found")

        try:
            async with session.get(pdf_link, headers=self.HEADERS, ssl=False, timeout=30) as r:
                if r.status != 200: return self.fallback_link(info, "PDF Error")
                pdf_bytes = await r.read()
        except: return self.fallback_link(info, "DL Error")

        try:
            data = {}
            current_header = "General"
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                    for line in text.split('\n'):
                        clean = line.strip()
                        if not clean: continue
                        lower = clean.lower()
                        is_h = any(x in lower for x in ["from ", " to ", "nicosia", "larnaca", "paphos"])
                        if is_h and len(clean) < 60 and not re.search(r'\d{1,2}[:.]\d{2}', clean):
                            current_header = clean.replace(":", "").title()
                            if current_header not in data: data[current_header] = []
                            continue
                        raw = self.extract_times(clean)
                        if raw:
                            if current_header not in data: data[current_header] = []
                            for t, stars in raw:
                                nt = self.normalize_time(t)
                                if "00:00" <= nt <= "23:59" and not any(x['t'] == nt for x in data[current_header]):
                                    data[current_header].append({"t": nt, "n": stars, "f": nt + stars})
            
            results = []
            for k, v in data.items():
                if v:
                    v.sort(key=lambda x: x['t'])
                    results.append({
                        "name": info['name'], "desc": k, "type": "all", "times": v,
                        "url": pdf_link, "prov": info['provider'], "notes": {}
                    })
            return results or self.fallback_link(info, "Empty PDF")
        except: return self.fallback_link(info, "Parse Error")

    def fallback_link(self, info, reason):
        label = "Открыть сайт ↗"
        if "kapnos" in info['url']: label = "Сайт (PDF не найден) ↗"
        return [{
            "name": info['name'], "desc": f"External Link ({reason})", "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": label, "url": info['url']}], 
            "url": info['url'], "prov": info['provider'], "notes": {}
        }]