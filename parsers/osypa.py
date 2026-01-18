import re
from .base import BaseParser

class OsypaParser(BaseParser):
    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []

        # Единый список всех времен с привязкой к заголовкам
        grouped_times = {}
        last_header = "Route Schedule" # Заголовок по умолчанию

        # Проходим по ВСЕМ элементам в порядке появления
        # Используем рекурсивный поиск всех строк
        all_elements = soup.find_all(text=True)

        for text in all_elements:
            txt = text.strip()
            if not txt: continue
            
            # Пропускаем очень длинные куски текста (явно не расписание)
            if len(txt) > 200: continue
            
            lower = txt.lower()

            # --- Эвристика заголовка ---
            # Если в строке есть буквы, но НЕТ цифр времени (xx:xx), считаем это потенциальным заголовком
            has_time = re.search(r'\d{1,2}[:.]\d{2}', txt)
            
            # Ключевые слова для заголовков
            is_header_kw = any(w in lower for w in ['from', 'departure', 'route', 'monday', 'sunday', 'daily'])
            
            # Если это похоже на заголовок (короткий текст, есть буквы, нет времени)
            if not has_time and len(txt) > 3 and (is_header_kw or len(txt) < 40):
                # Очищаем заголовок от мусора
                candidate = txt.replace(':', '').strip()
                # Если кандидат адекватный, обновляем текущий заголовок
                if len(candidate) > 2 and not candidate.isdigit():
                    last_header = candidate
                continue

            # --- Поиск времени ---
            raw_times = self.extract_times(txt)
            if raw_times:
                if last_header not in grouped_times:
                    grouped_times[last_header] = []
                
                for t, stars in raw_times:
                    nt = self.normalize_time(t)
                    # Минимальная валидация (просто чтобы это было похоже на время)
                    if len(nt) == 5 and nt[2] == ':':
                        # Проверяем на дубликаты в текущей группе
                        if not any(x['t'] == nt for x in grouped_times[last_header]):
                            grouped_times[last_header].append({
                                "t": nt,
                                "n": stars,
                                "f": nt + stars,
                                "note_txt": "" # Для Osypa пока пусто
                            })

        # Формируем итоговый результат
        for head, t_list in grouped_times.items():
            if not t_list: continue
            
            # Сортировка
            t_list.sort(key=lambda x: x['t'])
            
            # Если список времен слишком короткий (1 шт) и заголовок странный, возможно это мусор (телефон, часы работы)
            # Но лучше показать лишнее, чем не показать ничего.
            
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