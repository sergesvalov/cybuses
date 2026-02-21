import asyncio
import aiohttp
import time
from config import ROUTES

# Импортируем парсеры
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

class ScraperService:
    def __init__(self):
        self.parser_map = {
            "intercity": IntercityParser(),
            "osypa": OsypaParser(),
            "shuttle": ShuttleParser()
        }

    async def fetch_route(self, session, key, info):
        """
        Получает данные для одного маршрута.
        Оборачивает ошибки, чтобы падение одного сайта не ломало всё.
        """
        provider_key = info.get('provider')
        parser = self.parser_map.get(provider_key)
        
        if not parser:
            print(f"Unknown provider for {key}")
            return []

        print(f"[{provider_key.upper()}] Fetching: {info['name']}...")
        try:
            # Запускаем парсинг
            result = await parser.parse(session, info)
            
            # Если вернулся пустой список, можно вывести предупреждение
            if not result:
                print(f"Warning: No data found for {info['name']}")
                
            return result
        except Exception as e:
            print(f"!!! Critical Error in {key}: {e}")
            return None # Return None to indicate failure

    async def get_all_data(self):
        start_time = time.time()
        
        # Используем одну сессию на все запросы
        async with aiohttp.ClientSession() as session:
            tasks = []
            keys = []
            for key, info in ROUTES.items():
                task = asyncio.create_task(self.fetch_route(session, key, info))
                tasks.append(task)
                keys.append(key)
            
            # Ждем выполнения всех задач
            results = await asyncio.gather(*tasks)
        
        # Выпрямляем список списков, игнорируя None (ошибки парсинга)
        flat_data = []
        parsing_errors = False
        for res in results:
            if res is None:
                parsing_errors = True
            else:
                flat_data.extend(res)
        
        # Возвращаем флаг ошибок вместе с данными, чтобы CacheManager знал
        print(f">>> Update finished in {time.time() - start_time:.2f} s. Total routes: {len(flat_data)}")
        return flat_data, parsing_errors
