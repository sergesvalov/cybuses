from parsers.base import BaseParser

class IntercityParser(BaseParser):
    def __init__(self):
        # Initialize the parent class
        super().__init__()
        self.url = "https://intercity-buses.com/?wp=routes" 

    def get_data(self):
        """
        Concrete implementation for Intercity Buses.
        """
        print(f"DEBUG: Fetching {self.url}...")
        
        soup = self.get_soup(self.url)
        
        if not soup:
            return {"error": "Failed to load Intercity website"}

        # --- PARSING LOGIC ---
        
        data = {
            "provider": "Intercity Buses",
            "routes": []
        }

        # Example: Using the helper method to find all times on the page
        # In a real scenario, you would target specific <table> or <div> elements first
        text_content = soup.get_text()
        times = self.extract_times(text_content)
        notes = self.extract_notes(soup)

        # Storing results
        data["raw_times_sample"] = times[:10] # Show first 10 for verification
        data["notes"] = notes

        return data