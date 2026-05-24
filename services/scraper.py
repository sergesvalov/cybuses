import asyncio
import aiohttp
import time
import logging
from config import ROUTES

# Импортируем парсеры
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)
# Добавляем хэндлер, если его еще нет (на случай, если не настроен базовый конфиг)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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
            logger.warning(f"Unknown provider for {key}")
            return []

        url = info.get('url', 'No URL')
        logger.info(f"[{provider_key.upper()}] Fetching: {info['name']} from {url} ...")
        try:
            result = await parser.parse(session, info)
            
            if not result:
                logger.warning(f"[{provider_key.upper()}] No data found for {info['name']} (URL: {url})")
                return [{
                    "name": info['name'],
                    "desc": "Сбой загрузки расписания",
                    "type": "all",
                    "times": [],
                    "url": info['url'],
                    "prov": provider_key,
                    "hasError": True,
                    "errorMsg": "Временно недоступно (нет данных)"
                }]
                
            logger.info(f"[{provider_key.upper()}] Successfully parsed {len(result)} directions for {info['name']}")
            
            for item in result:
                if 'duration' not in item and 'duration' in info:
                    item['duration'] = info['duration']
                    
            return result
        except Exception as e:
            logger.error(f"[{provider_key.upper()}] Critical Error fetching {info['name']} at {url}: {e}", exc_info=True)
            return [{
                "name": info['name'],
                "desc": "Сбой загрузки расписания",
                "type": "all",
                "times": [],
                "url": info['url'],
                "prov": provider_key,
                "hasError": True,
                "errorMsg": f"Ошибка связи ({type(e).__name__})"
            }]

    async def get_all_data(self):
        start_time = time.time()
        logger.info(">>> Starting batch update of all routes...")
        
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
        logger.info(f">>> Update finished in {time.time() - start_time:.2f} s. Total routes extracted: {len(flat_data)}. Parsing errors: {parsing_errors}")
        return flat_data, parsing_errors
