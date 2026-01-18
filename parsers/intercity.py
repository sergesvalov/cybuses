from .base import BaseParser

class IntercityParser(BaseParser):
    async def parse(self, session, info):
        """
        Парсер для Intercity Buses.
        Исправлена ошибка с undefined и добавлено поле 'f'.
        """
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: 
            return []
        
        target = info['target']
        blocks = { "from_paphos": [], "to_paphos": [] }
        current_dir = None
        
        # Расширенный список тегов для поиска
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        
        for tag in tags:
            txt = tag.get_text(" ", strip=True).lower()
            
            # Определение направления (улучшенная логика)
            is_from_paphos = ("from paphos" in txt or "from pafos" in txt or 
                              f"paphos - {target}" in txt or f"pafos - {target}" in txt)
            
            is_to_paphos = (f"from {target}" in txt or 
                            f"{target} - paphos" in txt or f"{target} - pafos" in txt)

            # Переключаем текущее направление
            if is_from_paphos and len(txt) < 100:
                current_dir = "from_paphos"
                continue
            
            if is_to_paphos and len(txt) < 100:
                current_dir = "to_paphos"
                continue
            
            # Если направление выбрано, ищем время
            if current_dir:
                raw = self.extract_times(tag.get_text(" ", strip=True))
                # Эвристика: обычно в блоке расписания несколько времен сразу
                if len(raw) >= 1: # Ослабили проверку, чтобы брать даже одиночные строки
                    times_only = []
                    for t in raw:
                        norm_t = self.normalize_time(t[0])
                        note = t[1]
                        # ВАЖНО: Добавляем поле 'f' (formatted), которое ждет фронтенд
                        times_only.append({
                            "t": norm_t, 
                            "n": note,
                            "f": norm_t + note
                        })
                    
                    if times_only:
                        blocks[current_dir].append(times_only)

        # Маппинг ключей
        dir_titles = {
            "from_paphos": f"Paphos ➝ {info['name']}",
            "to_paphos": f"{info['name']} ➝ Paphos"
        }

        priority_order = ["from_paphos", "to_paphos"]

        for d_key in priority_order:
            b_list = blocks[d_key]
            if not b_list: continue

            # Логика слияния таблиц (0=Будни, 1=Выходные)
            weekday_t, weekend_t = [], []
            
            if len(b_list) == 1:
                weekday_t = b_list[0]
                weekend_t = b_list[0]
            else:
                weekday_t = b_list[0]
                weekend_t = b_list[1]
                # Если блоков больше (бывает 3-4 таблицы), добавляем их к будням
                if len(b_list) > 2:
                    for extra in b_list[2:]: 
                        weekday_t.extend(extra)

            def clean(lst):
                """Удаляем дубликаты и сортируем"""
                seen, res = set(), []
                for x in lst:
                    if x['t'] not in seen: 
                        res.append(x)
                        seen.add(x['t'])
                res.sort(key=lambda k: k['t'])
                return res

            final_wd = clean(weekday_t)
            final_we = clean(weekend_t)
            
            base_desc = dir_titles[d_key]

            # Если парсер нашел мусор, но не нашел времен — пропускаем
            if not final_wd and not final_we:
                continue

            results.append({
                "name": info['name'], "desc": base_desc, "type": "weekday",
                "times": final_wd, "url": info['url'], "prov": "intercity",
                "notes": {}
            })
            results.append({
                "name": info['name'], "desc": base_desc, "type": "weekend",
                "times": final_we, "url": info['url'], "prov": "intercity",
                "notes": {}
            })

        return results