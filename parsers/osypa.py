import re
from .base import BaseParser

class OsypaParser(BaseParser):
    async def parse(self, session, info):
        """
        Parses Osypa (Paphos City) bus schedules.
        Groups times by route headers found in the text.
        """
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: 
            return []

        groups = {}
        current_head = "Schedule"
        
        # Elements that might contain headers or times
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li'])
        
        for el in tags:
            txt = el.get_text(" ", strip=True)
            lower = txt.lower()
            
            # Detect Header (e.g., "From Harbour")
            if ("from " in lower or "departure " in lower) and len(txt) < 80 and not re.search(r'\d{1,2}[:.]\d{2}', txt):
                current_head = txt.replace(':', '').strip()
                if current_head not in groups: 
                    groups[current_head] = []
                continue
            
            # Detect Times
            raw = self.extract_times(txt)
            if raw:
                if current_head not in groups: 
                    groups[current_head] = []
                
                for t, stars in raw:
                    nt = self.normalize_time(t)
                    # Filter out invalid times (optional logic from original)
                    if "00:00" <= nt <= "02:00" or "04:30" <= nt <= "23:59":
                        # Deduplication
                        if not any(x['t'] == nt for x in groups[current_head]):
                            groups[current_head].append({"t": nt, "n": stars, "f": nt + stars})
        
        # Build Result Objects
        for head, t_list in groups.items():
            if t_list:
                t_list.sort(key=lambda x: x['t'])
                results.append({
                    "name": info['name'], 
                    "desc": head, 
                    "type": "all",
                    "times": t_list, 
                    "url": info['url'], 
                    "prov": "osypa", 
                    "notes": {}
                })
        return results