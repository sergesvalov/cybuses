import io
import re
import asyncio
import pdfplumber
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        url = info['url']
        
        # All our shuttle targets currently use direct PDF links
        if url.lower().endswith('.pdf'):
            return await self.process_pdf(session, url, info)

        return self.fallback_link(info, "No valid PDF link configured")

    async def process_pdf(self, session, pdf_url, info):
        try:
            async with session.get(pdf_url, headers=self.HEADERS, ssl=False, timeout=30) as r:
                if r.status != 200: return self.fallback_link(info, "PDF Access Error")
                pdf_bytes = await r.read()
        except Exception as e: 
            return self.fallback_link(info, f"Download Error: {e}")

        try:
            # Выполняем синхронный тяжелый парсинг в отдельном потоке
            results = await asyncio.to_thread(self.extract_limassol_express_logic, pdf_bytes, pdf_url, info)
            return results if results else self.fallback_link(info, "No data extracted")
        except Exception as e:
            print(f"PDF Error: {e}")
            return self.fallback_link(info, "Parse Error")

    def extract_limassol_express_logic(self, pdf_bytes, pdf_url, info):
        raw_results = []
        
        DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        schedule = { d: [] for d in DAYS }

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                
                # We expect the times to be in the last row of the table
                times_row = table[-1]
                if len(times_row) < 14:
                    continue
                
                # Days 0-4 are Monday-Friday
                # Days 5-6 are Saturday-Sunday
                
                for day_idx in range(7):
                    day_type = DAYS[day_idx]
                    
                    limassol_col = day_idx * 2
                    airport_col = limassol_col + 1
                    
                    if times_row[airport_col]:
                        for t_str, stars in self.extract_times(times_row[airport_col]):
                            nt = self.normalize_time(t_str)
                            if ":" in nt:
                                h, m = map(int, nt.split(':'))
                                if 0 <= h <= 23 and 0 <= m <= 59:
                                    if not any(x['t'] == nt for x in schedule[day_type]):
                                        schedule[day_type].append({
                                            "t": nt, "n": stars, "f": nt + stars, "note_txt": ""
                                        })

        # Format output
        for d_type in DAYS:
            t_list = schedule[d_type]
            if t_list:
                t_list.sort(key=lambda x: x['t'])
                raw_results.append({
                    "name": info['name'],
                    "desc": "Paphos Airport ➝ Larnaca Airport",
                    "type": d_type,
                    "times": t_list,
                    "url": pdf_url,
                    "prov": info['provider'],
                    "notes": {}
                })
        return raw_results

    def fallback_link(self, info, reason):
        return [{
            "name": info['name'], "desc": f"External Link ({reason})", "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": "Открыть сайт ↗", "url": info['url']}], 
            "url": info['url'], "prov": info['provider'], "notes": {}
        }]