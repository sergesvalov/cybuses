import json
import logging
from datetime import datetime

# Обязательно проверьте parsers/__init__.py!
try:
    from parsers.intercity import IntercityParser
    from parsers.osypa import OsypaParser
    from parsers.shuttle import ShuttleParser
except ImportError:
    # Заглушка, чтобы локально работало, даже если нет файлов
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BusScraper:
    def __init__(self, cache_file='bus_cache.json'):
        self.cache_file = cache_file
        # Инициализируем классы. 
        # Если вы еще не создали OsypaParser, закомментируйте лишнее
        self.parsers = {
            "intercity": IntercityParser(),
            # "osypa": OsypaParser(),   <-- Раскомментируйте, когда создадите файл
            # "shuttle": ShuttleParser() <-- Раскомментируйте, когда создадите файл
        }

    def fetch_all_data(self):
        all_data = {
            "last_updated": datetime.now().isoformat(),
            "providers": {}
        }

        for name, parser in self.parsers.items():
            logging.info(f"Запуск парсера: {name}")
            try:
                # ВЫЗОВ МЕТОДА ИЗ BASE.PY
                data = parser.get_data()
                all_data["providers"][name] = data
            except Exception as e:
                logging.error(f"Ошибка в {name}: {e}")
                all_data["providers"][name] = {"error": str(e)}

        self._save_to_cache(all_data)
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