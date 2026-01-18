import re
from .base import BaseParser

class IntercityParser(BaseParser):
    def extract_footnotes(self, soup):
        notes = {}
        tags = soup.find_all(['p', 'div', 'span', 'li', 'td'])
        for tag in tags:
            txt = tag.get_text(" ", strip=True)
            match = re.match(r'^(\*+)\s+(.+)', txt)
            if match:
                key = match.group(1)
                value = match.group(2)
                if len(value) > 3:
                    notes[key] = value
        return notes

    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []
        
        footnotes_map = self.extract_footnotes(soup)
        target = info['target']
        blocks = { "from_paphos": [], "to_paphos": [] }
        current_dir = None
        
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for tag in tags:
            txt = tag.get_text(" ", strip=True).lower()
            
            is_from_paphos = ("from paphos" in txt or "from pafos" in txt or 
                              f"paphos - {target}" in txt or f"pafos - {target}" in txt)
            is_to_paphos = (f"from {target}" in txt or 
                            f"{target} - paphos" in txt or f"{target} - pafos" in txt)

            if is_from_paphos and len(txt) < 100:
                current_dir = "from_paphos"; continue
            if is_to_paphos and len(txt) < 100:
                current_dir = "to_paphos"; continue
            
            if current_dir:
                raw = self.extract_times(tag.get_text(" ", strip=True))
                if len(raw) >= 1:
                    times_only = []
                    for t_tuple in raw:
                        t_str, stars = t_tuple[0], t_tuple[1]
                        norm_t = self.normalize_time(t_str)
                        note_text = footnotes_map.get(stars, "")
                        if stars and not note_text: note_text = "See route details on website"

                        times_only.append({
                            "t": norm_t, "n": stars, "f": norm_t + stars, "note_txt": note_text
                        })
                    if times_only: blocks[current_dir].append(times_only)

        dir_titles = {
            "from_paphos": f"Paphos ➝ {info['name']}",
            "to_paphos": f"{info['name']} ➝ Paphos"
        }
        
        for d_key in ["from_paphos", "to_paphos"]:
            b_list = blocks[d_key]
            if not b_list: continue
            merged_list = [x for sub in b_list for x in sub]
            
            seen, final_list = set(), []
            for x in merged_list:
                k = x['t'] + x['n']
                if k not in seen:
                    final_list.append(x); seen.add(k)
            final_list.sort(key=lambda k: k['t'])
            
            if not final_list: continue

            results.append({
                "name": info['name'], "desc": dir_titles[d_key], "type": "all",
                "times": final_list, "url": info['url'], "prov": "intercity", "notes": footnotes_map 
            })
        return results