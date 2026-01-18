import asyncio
import aiohttp
import time
from config import ROUTES

# Импортируем парсеры
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

PARSER_MAP = {
    "intercity": IntercityParser(),
    "osypa": OsypaParser(),
    "shuttle": ShuttleParser()
}

async def fetch_route(session, key, info):
    """
    Получает данные для одного маршрута.
    Оборачивает ошибки, чтобы падение одного сайта не ломало всё.
    """
    provider_key = info.get('provider')
    parser = PARSER_MAP.get(provider_key)
    
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
        return []

async def get_all_data_async():
    start_time = time.time()
    
    # Используем одну сессию на все запросы
    async with aiohttp.ClientSession() as session:
        tasks = []
        for key, info in ROUTES.items():
            task = asyncio.create_task(fetch_route(session, key, info))
            tasks.append(task)
        
        # Ждем выполнения всех задач
        results = await asyncio.gather(*tasks)
    
    # Выпрямляем список списков
    flat_data = [item for sublist in results for item in sublist]
    
    print(f">>> Update finished in {time.time() - start_time:.2f} s. Total routes: {len(flat_data)}")
    return flat_data