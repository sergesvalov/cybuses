import re
from .base import BaseParser

class IntercityParser(BaseParser):
    def extract_footnotes(self, soup):
        """
        Ищет тексты сносок на странице.
        Возвращает словарь: {'*': 'Текст сноски...', '**': 'Другой текст...'}
        """
        notes = {}
        # Ищем все текстовые блоки, которые начинаются с *
        # Обычно они лежат в <p> или <div> внизу страницы
        tags = soup.find_all(['p', 'div', 'span', 'li', 'td'])
        for tag in tags:
            txt = tag.get_text(" ", strip=True)
            # Регулярка: ищем начало строки вида "* Текст" или "** Текст"
            match = re.match(r'^(\*+)\s+(.+)', txt)
            if match:
                key = match.group(1)   # "*" или "**"
                value = match.group(2) # Сам текст
                # Сохраняем, если текст длиннее 3 символов (защита от мусора)
                if len(value) > 3:
                    notes[key] = value
        return notes

    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []
        
        # 1. Сначала собираем словарь сносок
        footnotes_map = self.extract_footnotes(soup)
        
        target = info['target']
        blocks = { "from_paphos": [], "to_paphos": [] }
        current_dir = None
        
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for tag in tags:
            txt = tag.get_text(" ", strip=True).lower()
            
            # Логика определения направления (без изменений)
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
                        t_str = t_tuple[0]
                        stars = t_tuple[1] # Это "*" или "**"
                        
                        norm_t = self.normalize_time(t_str)
                        
                        # ВАЖНО: Находим текст сноски по количеству звезд
                        # Если нет точного совпадения, пробуем найти частичное или пишем "Note"
                        note_text = footnotes_map.get(stars, "")
                        if stars and not note_text:
                            # Фолбек: если текст не найден, пишем "Special route"
                            note_text = "See route details on website"

                        times_only.append({
                            "t": norm_t, 
                            "n": stars,
                            "f": norm_t + stars,
                            "note_txt": note_text # Новое поле с текстом
                        })
                    
                    if times_only:
                        blocks[current_dir].append(times_only)

        # Сборка результатов
        dir_titles = {
            "from_paphos": f"Paphos ➝ {info['name']}",
            "to_paphos": f"{info['name']} ➝ Paphos"
        }
        priority_order = ["from_paphos", "to_paphos"]

        for d_key in priority_order:
            b_list = blocks[d_key]
            if not b_list: continue

            # Упрощенная логика слияния: берем все блоки
            # Часто на сайте таблицы разбиты криво, лучше слить все в один список и убрать дубли
            merged_list = []
            for sublist in b_list:
                merged_list.extend(sublist)

            # Дедупликация с сохранением note_txt
            seen = set()
            final_list = []
            for x in merged_list:
                unique_key = x['t'] + x['n']
                if unique_key not in seen:
                    final_list.append(x)
                    seen.add(unique_key)
            
            final_list.sort(key=lambda k: k['t'])

            if not final_list: continue

            # Интерсити обычно не делит на будни/выходные явно в HTML так, чтобы это легко парсилось
            # Поэтому возвращаем тип 'all' (ежедневно), либо можно оставить старую логику
            results.append({
                "name": info['name'], 
                "desc": dir_titles[d_key], 
                "type": "all",
                "times": final_list, 
                "url": info['url'], 
                "prov": "intercity",
                "notes": footnotes_map 
            })

        return results