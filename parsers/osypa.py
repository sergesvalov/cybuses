import re
from .base import BaseParser


def resolve_osypa_direction(route_name: str, dir_text: str) -> str:
    """Converts OSYPA stop/direction text into standardized 'Origin ➝ Destination' format."""
    dl = dir_text.lower()
    if '612' in route_name:
        if 'airport' in dl:
            return 'Pafos Airport ➝ Tombs of the Kings (Paphos)'
        return 'Tombs of the Kings (Paphos) ➝ Pafos Airport'
    elif '613' in route_name:
        if 'airport' in dl:
            return 'Pafos Airport ➝ Karavella (Paphos)'
        return 'Karavella (Paphos) ➝ Pafos Airport'
    elif '615' in route_name:
        if 'coral' in dl:
            return 'Coral Bay ➝ Tombs of the Kings (Paphos)'
        return 'Tombs of the Kings (Paphos) ➝ Coral Bay'
    elif '618' in route_name or '603' in route_name:
        if 'karavel' in dl:
            return 'Karavella (Paphos) ➝ Harbour (Paphos)'
        return 'Harbour (Paphos) ➝ Karavella (Paphos)'
    elif '610' in route_name:
        if 'market' in dl:
            return 'Municipal Market (Paphos) ➝ Harbour (Paphos)'
        return 'Harbour (Paphos) ➝ Municipal Market (Paphos)'
    elif '611' in route_name:
        if 'waterpark' in dl or 'beach' in dl:
            return 'Waterpark ➝ Tombs of the Kings (Paphos)'
        return 'Tombs of the Kings (Paphos) ➝ Waterpark'
    elif '631' in route_name:
        if 'petra' in dl:
            return 'Petra tou Romiou ➝ Harbour (Paphos)'
        return 'Harbour (Paphos) ➝ Petra tou Romiou'
    return dir_text


class OsypaParser(BaseParser):
    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup:
            return []

        grouped_times = {}
        current_direction = ""
        current_day_type = "all"

        all_elements = soup.find_all(string=True)

        for text in all_elements:
            txt = text.strip()
            if not txt or len(txt) > 800:
                continue

            lower = txt.lower()
            has_time = re.search(r'\b\d{1,2}[:.]\d{2}\b', txt)

            is_from_header = lower.startswith('from ') or any(
                k in lower for k in [
                    'tombs of the kings', 'karavela', 'karavella', 'harbour',
                    'pafos airport', 'coral bay', 'municipal market',
                    'waterpark', 'petra tou romiou'
                ]
            )

            is_day_kw = any(w in lower for w in ['monday', 'sunday', 'daily', 'saturday', 'friday', 'weekend', 'weekday'])

            if not has_time and len(txt) > 2 and len(txt) < 80:
                if is_from_header and not is_day_kw:
                    current_direction = resolve_osypa_direction(info['name'], txt)
                    continue

                if is_day_kw:
                    if ("monday" in lower and "sunday" in lower) or "daily" in lower:
                        current_day_type = "all"
                    elif "monday" in lower and "friday" in lower:
                        current_day_type = "weekday"
                    elif "saturday" in lower or "sunday" in lower:
                        current_day_type = "weekend"
                    else:
                        current_day_type = "all"
                    continue

            raw_times = self.extract_times(txt)
            if raw_times:
                direction_label = current_direction or resolve_osypa_direction(info['name'], 'From ' + info['name'])
                key = (direction_label, current_day_type)
                if key not in grouped_times:
                    grouped_times[key] = []
                for t, stars in raw_times:
                    nt = self.normalize_time(t)
                    if len(nt) == 5 and nt[2] == ':':
                        if not any(x['t'] == nt for x in grouped_times[key]):
                            grouped_times[key].append({
                                "t": nt, "n": stars, "f": f"{nt}{stars}", "note_txt": ""
                            })

        for (dir_label, d_type), t_list in grouped_times.items():
            if not t_list:
                continue
            t_list.sort(key=lambda x: x['t'])
            results.append({
                "name": info['name'],
                "desc": dir_label,
                "type": d_type,
                "times": t_list,
                "url": info['url'],
                "prov": "osypa",
                "notes": {}
            })
        return results