from .base import BaseParser

class ShuttleParser(BaseParser):
    def parse(self, info):
        link_txt = "Открыть сайт ↗" if "kapnos" in info['url'] else "Скачать PDF ↗"
        return [{
            "name": info['name'], 
            "desc": "Внешняя ссылка", 
            "type": "all", 
            "times": [{"t": "LINK", "n": "", "f": link_txt}], 
            "url": info['url'], 
            "prov": info['provider'], 
            "notes": {}
        }]