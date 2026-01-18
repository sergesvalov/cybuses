from .base import BaseParser

class IntercityParser(BaseParser):
    def parse(self, info):
        results = []
        soup = self.get_soup(info['url'])
        if not soup: return []
        
        notes = self.extract_notes(soup)
        target = info['target']
        
        blocks = { "from_paphos": [], "to_paphos": [] }
        current_dir = None
        
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for tag in tags:
            txt = tag.get_text(" ", strip=True).lower()
            
            # Направления
            if (("from paphos" in txt or "from pafos" in txt) or 
                (f"paphos - {target}" in txt) or (f"pafos - {target}" in txt)) and len(txt) < 100:
                current_dir = "from_paphos"; continue
            
            if ((f"from {target}" in txt) or (f"{target} - paphos" in txt) or 
                (f"{target} - pafos" in txt)) and len(txt) < 100:
                current_dir = "to_paphos"; continue
            
            if current_dir:
                raw = self.extract_times(tag.get_text(" ", strip=True))
                if len(raw) >= 3:
                    times_only = [{"t": self.normalize_time(t), "n": s, "f": self.normalize_time(t)+s} for t, s in raw]
                    
                    # Дедупликация
                    current_sig = ",".join([x['t'] for x in times_only])
                    existing_sigs = [",".join([x['t'] for x in blk]) for blk in blocks[current_dir]]
                    if current_sig not in existing_sigs:
                        blocks[current_dir].append(times_only)

        # Сборка
        priority_order = ["from_paphos", "to_paphos"]
        dir_titles = {
            "from_paphos": f"👉 Из Пафоса -> {target.capitalize()}",
            "to_paphos": f"👈 Из {target.capitalize()} -> Пафос"
        }

        for d_key in priority_order:
            b_list = blocks[d_key]
            if not b_list: continue

            # Слияние таблиц (0=Будни, 1=Выходные, Остальные->Будни)
            weekday_t, weekend_t = [], []
            
            if len(b_list) == 1:
                weekday_t = b_list[0]; weekend_t = b_list[0]
            else:
                weekday_t = b_list[0]; weekend_t = b_list[1]
                if len(b_list) > 2:
                    for extra in b_list[2:]: weekday_t.extend(extra)

            def clean(lst):
                seen, res = set(), []
                for x in lst:
                    if x['t'] not in seen: res.append(x); seen.add(x['t'])
                res.sort(key=lambda k: k['t'])
                return res

            final_wd = clean(weekday_t)
            final_we = clean(weekend_t)
            
            base_desc = dir_titles[d_key]

            results.append({
                "name": info['name'], "desc": base_desc, "type": "weekday",
                "times": final_wd, "url": info['url'], "prov": "intercity",
                "notes": {k: v for k, v in notes.items() if k in [x['n'] for x in final_wd]}
            })
            results.append({
                "name": info['name'], "desc": base_desc, "type": "weekend",
                "times": final_we, "url": info['url'], "prov": "intercity",
                "notes": {k: v for k, v in notes.items() if k in [x['n'] for x in final_we]}
            })

        return results