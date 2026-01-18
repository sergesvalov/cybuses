import json
import logging
import os
from datetime import datetime

# Import individual parsers
# Ensure that parsers/__init__.py exists in the parsers directory!
try:
    from parsers.intercity import IntercityParser
    from parsers.osypa import OsypaParser
    from parsers.shuttle import ShuttleParser
except ImportError as e:
    logging.error(f"Import error: {e}. Check if parsers/__init__.py exists.")
    raise

# Configure logging for Docker (outputs to stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BusScraper:
    def __init__(self, cache_file='bus_cache.json'):
        self.cache_file = cache_file
        # Initialize parser instances
        self.parsers = {
            "intercity": IntercityParser(),
            "osypa": OsypaParser(),
            "shuttle": ShuttleParser()
        }

    def fetch_all_data(self):
        """
        Runs all parsers and saves aggregated results to a JSON cache.
        """
        all_data = {
            "last_updated": datetime.now().isoformat(),
            "providers": {}
        }

        for name, parser in self.parsers.items():
            logging.info(f"Starting scraper for: {name}")
            try:
                # Get data from the specific parser
                data = parser.get_data()
                all_data["providers"][name] = data
                logging.info(f"Successfully updated {name}")
            except Exception as e:
                logging.error(f"Error scraping {name}: {str(e)}")
                all_data["providers"][name] = {"error": "Service unavailable", "data": []}

        self._save_to_cache(all_data)
        return all_data

    def _save_to_cache(self, data):
        """
        Writes the results to the local JSON file.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                # FIX: ensure_ascii (with underscore) is the correct parameter name
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Data saved to {self.cache_file}")
        except IOError as e:
            logging.error(f"File writing error: {e}")

# Helper function that main.py calls
def get_all_data():
    """
    Wrapper function to maintain compatibility with main.py imports.
    """
    scraper = BusScraper()
    return scraper.fetch_all_data()

if __name__ == "__main__":
    # If run directly, update the cache
    get_all_data()