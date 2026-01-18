import re
from .base import BaseParser

class OsypaParser(BaseParser):
    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []

        grouped_times = {}
        last_header = "Route Schedule"
        all_elements = soup.find_all(text=True)

        for text in all_elements:
            txt = text.strip()
            if not txt or len(txt) > 200: continue
            
            lower = txt.lower()
            has_time = re.search(r'\d{1,2}[:.]\d{2}', txt)
            is_header_kw = any(w in lower for w in ['from', 'departure', 'route', 'monday', 'sunday', 'daily'])
            
            if not has_time and len(txt) > 3 and (is_header_kw or len(txt) < 40):
                candidate = txt.replace(':', '').strip()
                if len(candidate) > 2 and not candidate.isdigit():
                    last_header = candidate
                continue

            raw_times = self.extract_times(txt)
            if raw_times:
                if last_header not in grouped_times: grouped_times[last_header] = []
                for t, stars in raw_times:
                    nt = self.normalize_time(t)
                    if len(nt) == 5 and nt[2] == ':':
                        if not any(x['t'] == nt for x in grouped_times[last_header]):
                            grouped_times[last_header].append({
                                "t": nt, "n": stars, "f": nt + stars, "note_txt": ""
                            })

        for head, t_list in grouped_times.items():
            if not t_list: continue
            t_list.sort(key=lambda x: x['t'])
            results.append({
                "name": info['name'], "desc": head, "type": "all",
                "times": t_list, "url": info['url'], "prov": "osypa", "notes": {}
            })
        return results