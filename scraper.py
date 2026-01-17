import time
import random
from config import ROUTES

# Импортируем классы парсеров
from parsers.intercity import IntercityParser
from parsers.osypa import OsypaParser
from parsers.shuttle import ShuttleParser

# Реестр парсеров: ключ из конфига -> Класс
PARSER_MAP = {
    "intercity": IntercityParser(),
    "osypa": OsypaParser(),
    "shuttle": ShuttleParser()
}

def get_all_data():
    all_data = []
    
    # Перемешиваем маршруты для имитации человека
    items = list(ROUTES.items())
    random.shuffle(items)
    
    for key, info in items:
        provider_key = info.get('provider')
        
        # Находим нужный парсер
        parser = PARSER_MAP.get(provider_key)
        
        if parser:
            print(f"[{provider_key.upper()}] Обновление: {info['name']}...")
            try:
                # ЗАПУСК ПАРСЕРА
                route_data = parser.parse(info)
                all_data.extend(route_data)
            except Exception as e:
                print(f"!!! Ошибка в {key}: {e}")
        else:
            print(f"Неизвестный провайдер для {key}")
            
        # Пауза
        time.sleep(random.uniform(1.0, 2.5))
        
    return all_data

if __name__ == "__main__":
    # Для теста можно запустить scraper.py отдельно
    import json
    data = get_all_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    