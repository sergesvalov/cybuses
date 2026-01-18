from parsers.base import BaseParser

class IntercityParser(BaseParser):
    def __init__(self):
        super().__init__()
        # URL страницы с расписанием
        self.url = "https://intercity-buses.com/?wp=routes" 

    def get_data(self):  # <--- БЫЛО: parse(self, info), СТАЛО: get_data(self)
        print(f"DEBUG: Загрузка {self.url}...") # Видно в логах Docker
        
        soup = self.get_soup(self.url)
        
        if not soup:
            return {"error": "Не удалось загрузить сайт Intercity"}

        # --- ЛОГИКА ПАРСИНГА ---
        # Пример: ищем все ссылки на маршруты или времена
        # Адаптируйте селекторы под реальный сайт
        
        data = {
            "provider": "Intercity Buses",
            "routes": []
        }

        # Пример сбора данных (замените на свои реальные селекторы)
        # Допустим, ищем таблицы или списки
        text_content = soup.get_text()
        times = self.extract_times(text_content)
        notes = self.extract_notes(soup)

        data["raw_times_found"] = times[:10] # Покажем первые 10 для проверки
        data["notes"] = notes

        return data