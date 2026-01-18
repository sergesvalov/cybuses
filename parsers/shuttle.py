from .base import BaseParser

class ShuttleParser(BaseParser):
    async def parse(self, session, info):
        """
        Static parser for Shuttle services. 
        Returns a link instead of a timetable.
        """
        link_txt = "Open Site ↗" if "kapnos" in info['url'] else "Download PDF ↗"
        
        return [{
            "name": info['name'], 
            "desc": "External Link", 
            "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": link_txt}], 
            "url": info['url'], 
            "prov": info['provider'], 
            "notes": {}
        }]