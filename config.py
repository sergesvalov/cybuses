# config.py
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://cybase:cybase@db:5432/cybase")

# Справочник маршрутов (какие парсить и какие города)
# provider: указывает, какой парсер использовать (intercity, osypa, shuttle)
# target: вспомогательный маркер для логики парсинга (city, airport, etc)

ROUTES = {
    # --- INTERCITY BUSES (Междугородние) ---
    "limassol": {
        "name": "Paphos ↔ Limassol", 
        "url": "https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/", 
        "city1": "paphos", 
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 15m"
    },
    "nicosia": {
        "name": "Paphos ↔ Nicosia", 
        "url": "https://intercity-buses.com/en/routes/nicosia-paphos-paphos-nicosia/", 
        "city1": "paphos", 
        "city2": "nicosia",
        "provider": "intercity",
        "duration": "~ 2h"
    },
    "larnaca": {
        "name": "Paphos ↔ Larnaca", 
        "url": "https://intercity-buses.com/en/routes/larnaca-limassol-paphos-paphos-limassol-larnaca/", 
        "city1": "paphos", 
        "city2": "larnaca",
        "provider": "intercity",
        "duration": "~ 2h"
    },
    "nicosia_limassol": {
        "name": "Nicosia ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/nicosia-limassol-limassol-nicosia/",
        "city1": "nicosia",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 45m"
    },
    "larnaca_limassol": {
        "name": "Larnaca ↔ Limassol",
        "url": "https://intercity-buses.com/en/routes/larnaca-limassol-limassol-larnaca/",
        "city1": "larnaca",
        "city2": "limassol",
        "provider": "intercity",
        "duration": "~ 1h 30m"
    },
    "larnaca_paralimni": {
        "name": "Larnaca ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/larnaca-ayia-napa-paralimni-paralimni-ayia-napa-larnaca/",
        "city1": "larnaca",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 1h 15m"
    },
    "nicosia_paralimni": {
        "name": "Nicosia ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/nicosia-ayia-napa-paralimni-ayia-napa-paralimni-nicosia/",
        "city1": "nicosia",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 1h 30m"
    },
    "paphos_paralimni": {
        "name": "Paphos ↔ Paralimni / Ayia Napa",
        "url": "https://intercity-buses.com/en/routes/paralimni-ayia-napa-larnaca-paphos-paphos-larnaca-ayia-napa-paralimni/",
        "city1": "paphos",
        "city2": "paralimni",
        "provider": "intercity",
        "duration": "~ 2h 45m"
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
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/612", 
        "target": "city", 
        "provider": "osypa",
        "duration": "~ 35m"
    },
    
    # --- AIRPORT SHUTTLES (Шаттлы) ---
    "kapnos": {
        "name": "Kapnos Airport", 
        "url": "https://kapnosairportshuttle.com/", 
        "target": "airport", 
        "provider": "shuttle",
        "duration": "~ 1h 30m"
    },
    # Парсер найдет PDF на странице расписаний
    "limassol_airport": {
        "name": "Limassol Airport Express", 
        "url": "https://limassolairportexpress.eu/?page_id=280", 
        "target": "airport", 
        "provider": "shuttle",
        "duration": "~ 50m"
    }
}