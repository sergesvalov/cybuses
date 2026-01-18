import json
import logging
from datetime import datetime

# Импорты (убедитесь, что файлы существуют)
try:
    from parsers.intercity import IntercityParser
    # from parsers.osypa import OsypaParser   # Раскомментируйте, когда добавите код
    # from parsers.shuttle import ShuttleParser # Раскомментируйте, когда добавите код
except ImportError as e:
    logging.error(f"Ошибка импорта парсеров: {e}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BusScraper:
    def __init__(self, cache_file='bus_cache.json'):
        self.cache_file = cache_file
        self.parsers = {
            "intercity": IntercityParser(),
            # "osypa": OsypaParser(),
            # "shuttle": ShuttleParser()
        }

    def fetch_all_data(self):
        all_data = {
            "last_updated": datetime.now().isoformat(),
            "providers": {}
        }

        for name, parser in self.parsers.items():
            logging.info(f"Запуск парсера: {name}")
            try:
                # ВЫЗОВ ИСПРАВЛЕННОГО МЕТОДА
                data = parser.get_data()
                all_data["providers"][name] = data
                logging.info(f"Успешно: {name}")
            except Exception as e:
                logging.error(f"Ошибка в {name}: {e}")
                # Если парсер упал, пишем ошибку в JSON, чтобы фронтенд знал
                all_data["providers"][name] = {"error": str(e)}

        self._save_to_cache(all_data)
        print(">>> Cache Updated") # Для наглядности в логах
        return all_data

    def _save_to_cache(self, data):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Ошибка записи кэша: {e}")

def get_all_data():
    return BusScraper().fetch_all_data()

if __name__ == "__main__":
    get_all_data()