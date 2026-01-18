import json
import logging
import os
from datetime import datetime

# Import individual parsers
# Ensure parsers/__init__.py exists in your folder!
try:
    from parsers.intercity import IntercityParser
    from parsers.osypa import OsypaParser
    from parsers.shuttle import ShuttleParser
except ImportError as e:
    logging.error(f"Import error: {e}. Make sure parsers/__init__.py exists.")
    raise

# Configure logging to output to Docker stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BusScraper:
    def __init__(self, cache_file='bus_cache.json'):
        self.cache_file = cache_file
        # Map provider names to their respective parser classes
        self.parsers = {
            "intercity": IntercityParser(),
            "osypa": OsypaParser(),
            "shuttle": ShuttleParser()
        }

    def fetch_all_data(self):
        """
        Triggers all parsers and aggregates data into a single dictionary.
        """
        all_data = {
            "last_updated": datetime.now().isoformat(),
            "providers": {}
        }

        for name, parser in self.parsers.items():
            logging.info(f"Starting crawl for provider: {name}")
            try:
                # Assuming each parser has a .get_data() method
                data = parser.get_data()
                all_data["providers"][name] = data
                logging.info(f"Successfully fetched data for {name}")
            except Exception as e:
                logging.error(f"Failed to fetch data for {name}: {str(e)}")
                all_data["providers"][name] = {"error": "Service unavailable", "data": []}

        self._save_to_cache(all_data)
        return all_data

    def _save_to_cache(self, data):
        """
        Saves the aggregated data to a JSON file for the API to read.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure-ascii=False, indent=4)
            logging.info(f"Cache updated successfully in {self.cache_file}")
        except IOError as e:
            logging.error(f"Could not write to cache file: {e}")

def run_scraper():
    """
    Entry point for the scheduled task or manual trigger.
    """
    scraper = BusScraper()
    return scraper.fetch_all_data()

if __name__ == "__main__":
    run_scraper()