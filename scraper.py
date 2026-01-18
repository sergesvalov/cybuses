import json
import logging
from datetime import datetime

# Import your parsers
# Ensure parsers/__init__.py exists!
try:
    from parsers.intercity import IntercityParser
    # from parsers.osypa import OsypaParser
    # from parsers.shuttle import ShuttleParser
except ImportError as e:
    logging.warning(f"Parser import failed: {e}")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BusScraper:
    def __init__(self, cache_file='bus_cache.json'):
        self.cache_file = cache_file
        self.parsers = {}
        
        # Initialize the Intercity parser if it was imported successfully
        if 'IntercityParser' in globals():
            self.parsers["intercity"] = IntercityParser()

    def fetch_all_data(self):
        """
        Runs all registered parsers and aggregates data into a JSON cache.
        """
        all_data = {
            "last_updated": datetime.now().isoformat(),
            "providers": {}
        }

        for name, parser in self.parsers.items():
            logging.info(f"Triggering parser: {name}")
            try:
                # Calls the standardized method from BaseParser
                data = parser.get_data()
                all_data["providers"][name] = data
                logging.info(f"Successfully updated: {name}")
            except Exception as e:
                logging.error(f"Error in {name}: {e}")
                all_data["providers"][name] = {"error": str(e)}

        self._save_to_cache(all_data)
        return all_data

    def _save_to_cache(self, data):
        """Writes the resulting dictionary to a local JSON file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info("Cache file updated.")
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")

# --- IMPORTANT: THIS IS WHERE THE FUNCTION IS DEFINED ---
def get_all_data():
    """
    Function used by main.py to trigger the scraping process.
    """
    scraper = BusScraper()
    return scraper.fetch_all_data()

if __name__ == "__main__":
    # If the script is run directly (python scraper.py), it updates the cache
    get_all_data()