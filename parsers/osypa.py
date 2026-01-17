import re
from .base import BaseParser

class OsypaParser(BaseParser):
    def parse(self, info):
        results = []
        soup = self.get_soup(info['url'])
        if not soup: return []

        groups = {}
        current_head = "Расписание"
        
        # Сканируем конечные элементы
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li'])
        
        for el in tags:
            txt = el.get_text(" ", strip=True)
            lower = txt.lower()
            
            # Поиск заголовка
            if ("from " in lower or "departure " in lower) and len(txt) < 80 and not re.search(r'\d{1,2}[:.]\d{2}', txt):
                current_head = txt.replace(':', '').strip()
                if current_head not in groups: groups[current_head] = []
                continue
            
            # Поиск времени
            raw = self.extract_times(txt)
            if raw:
                if current_head not in groups: groups[current_head] = []
                for t, stars in raw:
                    nt = self.normalize_time(t)
                    if "00:00" <= nt <= "02:00" or "04:30" <= nt <= "23:59":
                        # Дедупликация
                        if not any(x['t'] == nt for x in groups[current_head]):
                            groups[current_head].append({"t": nt, "n": stars, "f": nt + stars})
        
        for head, t_list in groups.items():
            if t_list:
                t_list.sort(key=lambda x: x['t'])
                results.append({
                    "name": info['name'], "desc": head, "type": "all",
                    "times": t_list, "url": info['url'], "prov": "osypa", "notes": {}
                })
        return results
    