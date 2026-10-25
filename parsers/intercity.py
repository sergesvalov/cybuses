import re
from bs4 import BeautifulSoup
from .base import BaseParser

CITIES_SORTED = [
    ('paralimni', 'Paralimni'),
    ('παραλιμνι', 'Paralimni'),
    ('παραλίμνι', 'Paralimni'),
    ('ayia napa', 'Ayia Napa'),
    ('agia napa', 'Ayia Napa'),
    ('αγια ναπα', 'Ayia Napa'),
    ('αγία νάπα', 'Ayia Napa'),
    ('limassol', 'Limassol'),
    ('λεμεσός', 'Limassol'),
    ('λεμεσό', 'Limassol'),
    ('λεμεσο', 'Limassol'),
    ('λεμεσος', 'Limassol'),
    ('nicosia', 'Nicosia'),
    ('λευκωσία', 'Nicosia'),
    ('λευκωσια', 'Nicosia'),
    ('larnaca', 'Larnaca'),
    ('λάρνακα', 'Larnaca'),
    ('λαρνακα', 'Larnaca'),
    ('paphos', 'Paphos'),
    ('pafos', 'Paphos'),
    ('πάφος', 'Paphos'),
    ('παφος', 'Paphos'),
    ('πάφο', 'Paphos'),
    ('παφο', 'Paphos'),
]



class IntercityParser(BaseParser):
    def clean_direction_title(self, raw_title: str, default_name: str = "") -> str:
        """Normalizes raw direction headers like 'ΛΑΡΝΑΚΑ → ΛΕΜΕΣΟΣ → ΠΑΦΟΣ' to 'Larnaca ➝ Paphos'."""
        if not raw_title:
            return default_name

        raw_lower = raw_title.lower()
        parts = re.split(r'\s*[→➝\-–—]\s*', raw_lower)
        if len(parts) >= 2:
            src_part = parts[0]
            dst_part = parts[-1]

            src = None
            for k, v in CITIES_SORTED:
                if k in src_part:
                    src = v
                    break

            dst = None
            for k, v in CITIES_SORTED:
                if k in dst_part:
                    dst = v
                    break

            if src and dst and src != dst:
                return f"{src} ➝ {dst}"

        # English regex fallback
        eng_match = re.search(r'([A-Za-z\s]+)\s*[→➝\-–—]\s*([A-Za-z\s]+)', raw_title)
        if eng_match:
            s = eng_match.group(1).strip().title()
            d = eng_match.group(2).strip().title()
            if s and d and s != d:
                return f"{s} ➝ {d}"

        return raw_title

    def extract_footnotes(self, soup):
        notes = {}
        tags = soup.find_all(['p', 'div', 'span', 'li', 'td', 'h6'])
        for tag in tags:
            text_blocks = tag.get_text("\n", strip=True).split("\n")
            for txt in text_blocks:
                txt = txt.strip()
                match = re.match(r'^(\*+|\d+)\s*(.+)', txt)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if len(value) > 3:
                        if key in notes:
                            if value not in notes[key]:
                                notes[key] += " " + value
                        else:
                            notes[key] = value
        return notes

    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup:
            return []

        # 1. Price extraction
        price_text = None
        for txt in soup.stripped_strings:
            if '€' in txt:
                match = re.search(r'€\s*\d+[.,]?\d*', txt)
                if match:
                    price_text = match.group(0)
                    break

        # 2. Duration extraction
        duration_text = info.get('duration')
        for h in soup.find_all(['h5', 'h6', 'p', 'div']):
            htxt = h.get_text(' ', strip=True).lower()
            if 'duration' in htxt or 'minutes approximately' in htxt or 'hours approximately' in htxt:
                m_dur = re.search(
                    r'(\d+\s*(?:hour|hours|hr|h)?\s*(?:&|and)?\s*\d+\s*(?:minutes|mins|m)?\s*approximately|\d+\s*hours?\s*approximately)',
                    htxt
                )
                if m_dur:
                    duration_text = f"~ {m_dur.group(1).replace('approximately', '').strip()}"
                    break

        # 3. Modern container detection: .dir-panel or .ic-direction-panel
        dir_panels = soup.find_all('div', class_=lambda c: c and any(x in c for x in ['dir-panel', 'ic-direction-panel']))

        if dir_panels:
            dir_titles_map = {}
            tab_containers = soup.find_all('div', class_=lambda c: c and any(x in c for x in ['dir-tabs', 'ic-direction-tabs']))
            for tc in tab_containers:
                for btn in tc.find_all(attrs={'data-dir': True}):
                    dir_titles_map[btn['data-dir']] = btn.get_text(' ', strip=True)
                for btn in tc.find_all(attrs={'data-direction': True}):
                    dir_titles_map[btn['data-direction']] = btn.get_text(' ', strip=True)

            for dp in dir_panels:
                dir_key = dp.get('data-dir') or dp.get('data-direction') or ''
                raw_title = dir_titles_map.get(dir_key, '')

                if not raw_title:
                    h = dp.find_previous(['h2', 'h3', 'h4'])
                    if h:
                        raw_title = h.get_text(' ', strip=True)

                desc = self.clean_direction_title(raw_title, default_name=info['name'])

                # Look for day-panels inside
                day_panels = dp.find_all('div', class_=lambda c: c and any(x in c for x in ['day-panel', 'ic-day-panel']))
                if not day_panels:
                    day_panels = [dp]

                for dayp in day_panels:
                    day_attr = dayp.get('data-day') or ''
                    day_title_el = dayp.find('div', class_='day-title') or dp.find('div', class_='day-title')
                    day_title_txt = day_title_el.get_text(' ', strip=True).lower() if day_title_el else ''

                    day_type = "daily"
                    if day_attr in ["weekday", "weekend"]:
                        day_type = day_attr
                    elif "monday" in day_title_txt and "friday" in day_title_txt:
                        day_type = "weekday"
                    elif "saturday" in day_title_txt or "sunday" in day_title_txt:
                        day_type = "weekend"

                    # Extract notes
                    notes = {}
                    notes_div = dayp.find('div', class_=lambda c: c and any(x in c for x in ['notes', 'ic-notes'])) or \
                                dp.find('div', class_=lambda c: c and any(x in c for x in ['notes', 'ic-notes']))
                    if notes_div:
                        for n in notes_div.find_all('div', class_=lambda c: c and any(x in c for x in ['note', 'ic-note'])):
                            ntxt = n.get_text(' ', strip=True)
                            m_n = re.match(r'^(\d+|\*+)\s*(.+)', ntxt)
                            if m_n:
                                notes[m_n.group(1)] = m_n.group(2)
                            elif ntxt:
                                notes["*"] = ntxt

                    # Extract times
                    times_div = dayp.find('div', class_=lambda c: c and any(x in c for x in ['times', 'ic-times']))
                    time_elements = times_div.find_all('div', class_=lambda c: c and any(x in c for x in ['time', 'ic-time'])) if times_div else []

                    times_list = []
                    for t_el in time_elements:
                        txt = t_el.get_text(' ', strip=True)
                        m_t = re.search(r'\b([01]?\d|2[0-3]):[0-5]\d\b', txt)
                        if not m_t:
                            continue
                        t_str = m_t.group(0)
                        if len(t_str) == 4 and t_str[1] == ':':
                            t_str = "0" + t_str

                        # Check for note symbol right after time
                        after_time = txt[m_t.end():].strip()
                        m_sym = re.match(r'^(\d+|\*+)', after_time)
                        sym = m_sym.group(1) if m_sym else ""

                        note_text = notes.get(sym, "")
                        times_list.append({
                            "t": t_str,
                            "n": sym,
                            "f": f"{t_str}{sym}",
                            "note_txt": note_text
                        })

                    if times_list:
                        times_list.sort(key=lambda x: x['t'])
                        results.append({
                            "name": info['name'],
                            "desc": desc,
                            "type": day_type,
                            "times": times_list,
                            "url": info['url'],
                            "prov": "intercity",
                            "notes": notes,
                            "price": price_text,
                            "duration": duration_text
                        })

            if results:
                return results

        # 4. Fallback for legacy layout
        footnotes_map = self.extract_footnotes(soup)
        city1 = info.get('city1', 'paphos').lower()
        city2 = info.get('city2', '').lower()
        blocks = {
            "dir1": {"daily": [], "weekday": [], "weekend": []},
            "dir2": {"daily": [], "weekday": [], "weekend": []}
        }
        current_dir = None
        current_type = "daily"

        tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])

        for tag in tags:
            if tag.name == 'div' and tag.find(['div', 'p', 'table', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                continue

            raw_txt = tag.get_text(" ", strip=True)
            txt = raw_txt.lower()
            norm_txt = txt.replace("–", "-").replace("—", "-")

            def check_match(source, dest, text):
                s_opts = [source]
                d_opts = [dest]
                if source == "paphos": s_opts += ["pafos", "πάφος", "πάφο"]
                if dest == "paphos": d_opts += ["pafos", "πάφος", "πάφο"]
                if source == "limassol": s_opts += ["λεμεσός", "λεμεσό"]
                if dest == "limassol": d_opts += ["λεμεσός", "λεμεσό"]
                if source == "nicosia": s_opts += ["λευκωσία"]
                if dest == "nicosia": d_opts += ["λευκωσία"]
                if source == "larnaca": s_opts += ["λάρνακα"]
                if dest == "larnaca": d_opts += ["λάρνακα"]
                if source == "paralimni": s_opts += ["παραλίμνι", "ayia napa", "αγία νάπα"]
                if dest == "paralimni": d_opts += ["παραλίμνι", "ayia napa", "αγία νάπα"]

                for s in s_opts:
                    if f"from {s}" in text or f"από {s}" in text:
                        return True
                    for d in d_opts:
                        if s in text and d in text:
                            pos_s = text.find(s)
                            pos_d = text.find(d)
                            if pos_s != -1 and pos_d != -1 and pos_s < pos_d:
                                return True
                return False

            is_dir1 = check_match(city1, city2, norm_txt)
            is_dir2 = check_match(city2, city1, norm_txt)

            if is_dir1 and not is_dir2 and len(txt) < 100:
                current_dir = "dir1"
                current_type = "daily"
                continue
            if is_dir2 and not is_dir1 and len(txt) < 100:
                current_dir = "dir2"
                current_type = "daily"
                continue

            if len(norm_txt) < 100:
                if "monday" in norm_txt and "sunday" in norm_txt:
                    current_type = "daily"
                elif "monday" in norm_txt and "friday" in norm_txt:
                    current_type = "weekday"
                elif "saturday" in norm_txt or "sunday" in norm_txt or "public holiday" in norm_txt:
                    current_type = "weekend"
                elif "daily" in norm_txt:
                    current_type = "daily"

            if current_dir:
                # Heal spaces inside times
                healed = re.sub(r'(\d{1,2}:\d)\s*[:.]?\s*(\d)', r'\1\2', raw_txt)
                raw_times = self.extract_times(healed)
                if raw_times:
                    times_only = []
                    for t_tuple in raw_times:
                        t_str, stars = t_tuple[0], t_tuple[1]
                        norm_t = self.normalize_time(t_str)
                        note_text = footnotes_map.get(stars, "")
                        times_only.append({
                            "t": norm_t, "n": stars, "f": norm_t + stars, "note_txt": note_text
                        })
                    if times_only:
                        blocks[current_dir][current_type].append(times_only)

        dir_titles = {
            "dir1": f"{city1.title()} ➝ {city2.title()}",
            "dir2": f"{city2.title()} ➝ {city1.title()}"
        }

        for d_key in ["dir1", "dir2"]:
            for t_key in ["daily", "weekday", "weekend"]:
                b_list = blocks[d_key][t_key]
                if not b_list:
                    continue
                merged = [x for sub in b_list for x in sub]
                seen, final_list = set(), []
                for x in merged:
                    k = x['t'] + x['n']
                    if k not in seen:
                        final_list.append(x)
                        seen.add(k)
                final_list.sort(key=lambda k: k['t'])

                if final_list:
                    results.append({
                        "name": info['name'],
                        "desc": dir_titles[d_key],
                        "type": t_key,
                        "times": final_list,
                        "url": info['url'],
                        "prov": "intercity",
                        "notes": footnotes_map,
                        "price": price_text,
                        "duration": duration_text
                    })

        return results