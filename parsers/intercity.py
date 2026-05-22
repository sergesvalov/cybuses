import re
from .base import BaseParser

class IntercityParser(BaseParser):
    def extract_footnotes(self, soup):
        notes = {}
        tags = soup.find_all(['p', 'div', 'span', 'li', 'td'])
        for tag in tags:
            text_blocks = tag.get_text("\n", strip=True).split("\n")
            for txt in text_blocks:
                txt = txt.strip()
                match = re.match(r'^(\*+)\s*(.+)', txt)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if len(value) > 3:
                        if key in notes:
                            if value not in notes[key]: # Prevent duplicate appended notes
                                notes[key] += " " + value
                        else:
                            notes[key] = value
        return notes

    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []
        
        # 1. Попытка вытащить цену (ищем первую попавшуюся сумму с евро)
        price_text = None
        for txt in soup.stripped_strings:
            if '€' in txt:
                match = re.search(r'€\s*\d+[.,]?\d*', txt)
                if match:
                    price_text = match.group(0)
                    break

        footnotes_map = self.extract_footnotes(soup)
        city1 = info.get('city1', 'paphos')
        city2 = info.get('city2', '')
        blocks = { "dir1": [], "dir2": [] }
        current_dir = None
        
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for tag in tags:
            # Предотвращаем чтение крупных div-оберток (иначе смешиваются табы с расписанием)
            if tag.name == 'div' and tag.find(['div', 'p', 'table', 'ul', 'h2', 'h3']):
                continue

            txt = tag.get_text(" ", strip=True).lower()
            norm_txt = txt.replace("–", "-").replace("—", "-")
            
            def check_match(source, dest, text):
                s_opts = ["paphos", "pafos"] if source == "paphos" else [source]
                d_opts = ["paphos", "pafos"] if dest == "paphos" else [dest]
                for s in s_opts:
                    if f"from {s}" in text: return True
                    for d in d_opts:
                        if f"{s} - {d}" in text or f"{s}-{d}" in text: return True
                return False

            is_dir1 = check_match(city1, city2, norm_txt)
            is_dir2 = check_match(city2, city1, norm_txt)

            if is_dir1 and not is_dir2 and len(txt) < 100:
                current_dir = "dir1"; continue
            if is_dir2 and not is_dir1 and len(txt) < 100:
                current_dir = "dir2"; continue
            
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
            "dir1": f"{city1.title()} ➝ {city2.title()}",
            "dir2": f"{city2.title()} ➝ {city1.title()}"
        }
        
        for d_key in ["dir1", "dir2"]:
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
                "times": final_list, "url": info['url'], "prov": "intercity", "notes": footnotes_map,
                "price": price_text
            })
        return results