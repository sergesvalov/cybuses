import re
from .base import BaseParser

class OsypaParser(BaseParser):
    async def parse(self, session, info):
        """
        Парсер для городских автобусов (OSYPA).
        """
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: 
            return []

        groups = {}
        current_head = "Schedule"
        
        # Добавил 'div' в список тегов, так как современная верстка часто использует их
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for el in tags:
            # Убираем лишние пробелы и переносы
            txt = el.get_text(" ", strip=True)
            if not txt: continue
            
            lower = txt.lower()
            
            # --- Логика поиска заголовка ---
            # Ищем ключевые слова "From" или "Departure"
            # Если строка короткая (<100) и в ней НЕТ времени - это точно заголовок
            has_times = bool(re.search(r'\d{1,2}[:.]\d{2}', txt))
            
            is_header_candidate = ("from " in lower or "departure " in lower or "καραβέλα" in lower or "harbour" in lower)
            
            if is_header_candidate and not has_times and len(txt) < 100:
                current_head = txt.replace(':', '').strip()
                if current_head not in groups: 
                    groups[current_head] = []
                continue

            # --- Логика поиска времени ---
            raw = self.extract_times(txt)
            if raw:
                # Если в одной строке есть и "From ...", и время (например "From Karavella: 08:00, 09:00")
                # То используем начало строки как заголовок
                if is_header_candidate and len(txt) < 200:
                    # Пытаемся вытащить название до первого двоеточия или цифры
                    possible_head = re.split(r'[:\d]', txt)[0].strip()
                    if len(possible_head) > 3:
                        current_head = possible_head

                if current_head not in groups: 
                    groups[current_head] = []
                
                for t, stars in raw:
                    nt = self.normalize_time(t)
                    
                    # Фильтрация некорректных времен (иногда парсятся телефоны или годы)
                    # Разрешаем 00:00-02:00 (ночные) и 04:00-23:59
                    # Если попадет мусор типа "2024", он отсеется
                    if (nt >= "00:00" and nt <= "02:30") or (nt >= "04:00" and nt <= "23:59"):
                        # Дедупликация (чтобы не добавлять одно и то же время из вложенных тегов)
                        if not any(x['t'] == nt for x in groups[current_head]):
                            groups[current_head].append({
                                "t": nt, 
                                "n": stars, 
                                "f": nt + stars # Поле для фронтенда
                            })

        # Формируем итоговый список
        for head, t_list in groups.items():
            if t_list:
                t_list.sort(key=lambda x: x['t'])
                results.append({
                    "name": info['name'], 
                    "desc": head,        # Название направления
                    "type": "all",       # У городских обычно одно расписание (или сложно разделить)
                    "times": t_list, 
                    "url": info['url'], 
                    "prov": "osypa", 
                    "notes": {}
                })
        
        return results