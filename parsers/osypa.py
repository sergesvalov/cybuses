import re
from .base import BaseParser


class OsypaParser(BaseParser):
    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup:
            return []

        grouped_times = {}
        last_header = "Route Schedule"
        last_day_type = "all"
        all_elements = soup.find_all(string=True)

        for text in all_elements:
            txt = text.strip()
            if not txt or len(txt) > 800:
                continue

            lower = txt.lower()
            has_time = re.search(r'\d{1,2}[:.]\d{2}', txt)
            is_header_kw = any(w in lower for w in ['from', 'departure', 'route', 'monday', 'sunday', 'daily', 'saturday'])

            if not has_time and len(txt) > 3 and (is_header_kw or len(txt) < 40):
                candidate = txt.replace('–', '-').replace('—', '-').replace(':', '').strip()
                if len(candidate) > 2 and not candidate.isdigit():
                    last_header = candidate
                    cand_lower = candidate.lower()
                    if ("monday" in cand_lower and "sunday" in cand_lower) or "daily" in cand_lower:
                        last_day_type = "all"
                    elif "monday" in cand_lower and "friday" in cand_lower:
                        last_day_type = "weekday"
                    elif "saturday" in cand_lower or "sunday" in cand_lower:
                        last_day_type = "weekend"
                    else:
                        last_day_type = "all"
                continue

            raw_times = self.extract_times(txt)
            if raw_times:
                key = (last_header, last_day_type)
                if key not in grouped_times:
                    grouped_times[key] = []
                for t, stars in raw_times:
                    nt = self.normalize_time(t)
                    if len(nt) == 5 and nt[2] == ':':
                        if not any(x['t'] == nt for x in grouped_times[key]):
                            grouped_times[key].append({
                                "t": nt, "n": stars, "f": f"{nt}{stars}", "note_txt": ""
                            })

        for (head, d_type), t_list in grouped_times.items():
            if not t_list:
                continue
            t_list.sort(key=lambda x: x['t'])
            results.append({
                "name": info['name'],
                "desc": head,
                "type": d_type,
                "times": t_list,
                "url": info['url'],
                "prov": "osypa",
                "notes": {}
            })
        return results