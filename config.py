# config.py

# Настройка маршрутов
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
        "url": "https://intercity-buses.com/en/routes/%ce%bb%ce%ac%cf%81%ce%bd%ce%b1%ce%ba%ce%b1-%cf%80%ce%ac%cf%86%ce%bf%cf%82-%cf%80%ce%ac%cf%86%ce%bf%cf%82-%ce%bb%ce%ac%cf%81%ce%bd%ce%b1%ce%ba%ce%b1-%ce%b1%ce%b3%ce%af%ce%b1-%ce%bd%ce%ac%cf%80/", 
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