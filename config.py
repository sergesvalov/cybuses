# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://cybase:cybase@172.17.0.1:5432/cybase")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8999"))

# Справочник маршрутов (какие парсить и какие города)
# provider: указывает, какой парсер использовать (intercity, osypa, shuttle)
# target: вспомогательный маркер для логики парсинга (city, airport, etc)

ROUTES = {
    # --- INTERCITY BUSES (Междугородние) ---
    "limassol": {
        "name": "Paphos ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/limpafnew/",
        "city1": "paphos",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 15m"
    },
    "nicosia": {
        "name": "Paphos ↔ Nicosia",
        "url": "https://intercity-buses.com/en/routes/nicpafnew/",
        "city1": "paphos",
        "city2": "nicosia",
        "provider": "intercity",
        "duration": "~ 2h"
    },
    "larnaca": {
        "name": "Paphos ↔ Larnaca",
        "url": "https://intercity-buses.com/en/routes/larlimpafnew/",
        "city1": "paphos",
        "city2": "larnaca",
        "provider": "intercity",
        "duration": "~ 2h 45m"
    },
    "nicosia_limassol": {
        "name": "Nicosia ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/niclimnew/",
        "city1": "nicosia",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 45m"
    },
    "nicosia_larnaca": {
        "name": "Nicosia ↔ Larnaca",
        "url": "https://intercity-buses.com/en/routes/niclarnew/",
        "city1": "nicosia",
        "city2": "larnaca",
        "provider": "intercity",
        "duration": "~ 1h 15m"
    },
    "larnaca_limassol": {
        "name": "Larnaca ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/larlimnew/",
        "city1": "larnaca",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 30m"
    },
    "larnaca_paralimni": {
        "name": "Larnaca ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/larparnew/",
        "city1": "larnaca",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 1h 15m"
    },
    "nicosia_paralimni": {
        "name": "Nicosia ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/nicparnew/",
        "city1": "nicosia",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 2h"
    },
    "paphos_paralimni": {
        "name": "Paphos ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/parpafnew/",
        "city1": "paphos",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 3h"
    },
    "paralimni_limassol": {
        "name": "Paralimni / Ayia Napa ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/parlimnew/",
        "city1": "paralimni",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 2h"
    },

    # --- OSYPA (Городские автобусы Пафоса) ---
    "osypa_618": {
        "name": "618: Harbour - Karavella",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/618",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 15m"
    },
    "osypa_603": {
        "name": "603: Harbour - Karavella",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 25m"
    },
    "osypa_610": {
        "name": "610: Harbour - Market",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/610",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 15m"
    },
    "osypa_611": {
        "name": "611: Harbour - Waterpark",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/611",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 15m"
    },
    "osypa_615": {
        "name": "615: Harbour - Coral Bay",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/615",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 35m"
    },
    "osypa_631": {
        "name": "631: Harbour - Petra Romiou",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/631",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 45m"
    },
    "osypa_airport": {
        "name": "612: Harbour - Airport",
        "url": "https://www.pafosbuses.com/pafos-airport-bus-routes-1/612",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 35m"
    },
    "osypa_airport_613": {
        "name": "613: Karavella - Airport",
        "url": "https://www.pafosbuses.com/pafos-airport-bus-routes-1/613",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 40m"
    },

    # --- AIRPORT SHUTTLES (Шаттлы) ---
    "kapnos": {
        "name": "Kapnos Airport Shuttle",
        "url": "https://booking.kapnosairportshuttle.com/coachtrip/?page=routesandfares",
        "target": "airport",
        "provider": "shuttle",
        "duration": "~ 1h 30m"
    },
    "limassol_airport": {
        "name": "Limassol Airport Express",
        "url": "https://limassolairportexpress.eu/?page_id=280",
        "target": "airport",
        "provider": "shuttle",
        "duration": "~ 50m"
    }
}