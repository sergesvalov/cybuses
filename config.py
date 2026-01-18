# config.py

# Настройка маршрутов
# provider: указывает, какой парсер использовать (intercity, osypa, shuttle)
# target: вспомогательный маркер для логики парсинга (city, airport, etc)

ROUTES = {
    # --- INTERCITY BUSES (Междугородние) ---
    "limassol": {
        "name": "Limassol", 
        "url": "https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/", 
        "target": "limassol", 
        "provider": "intercity"
    },
    "nicosia": {
        "name": "Nicosia", 
        "url": "https://intercity-buses.com/en/routes/nicosia-paphos-paphos-nicosia/", 
        "target": "nicosia", 
        "provider": "intercity"
    },
    "larnaca": {
        "name": "Larnaca", 
        "url": "https://intercity-buses.com/en/routes/larnaca-paphos-paphos-larnaca/", 
        "target": "larnaca", 
        "provider": "intercity"
    },
    
    # --- OSYPA (Городские автобусы Пафоса) ---
    "osypa_618": {
        "name": "618: Harbour - Karavella", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/618", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_603": {
        "name": "603: Harbour - Karavella", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_610": {
        "name": "610: Harbour - Market", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/610", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_611": {
        "name": "611: Harbour - Waterpark", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/611", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_615": {
        "name": "615: Harbour - Coral Bay", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/615", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_631": {
        "name": "631: Harbour - Petra Romiou", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/631", 
        "target": "city", 
        "provider": "osypa"
    },
    "osypa_airport": {
        "name": "612: Harbour - Airport", 
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/612", 
        "target": "city", 
        "provider": "osypa"
    },
    
    # --- AIRPORT SHUTTLES (Шаттлы) ---
    "kapnos": {
        "name": "Kapnos Airport", 
        "url": "https://kapnosairportshuttle.com/", 
        "target": "airport", 
        "provider": "shuttle"
    },
    # Прямая ссылка на PDF расписание Limassol Airport Express
    "limassol_airport": {
        "name": "Limassol Airport Express", 
        "url": "https://limassolairportexpress.eu/wp-content/uploads/2025/11/Paphos-Itinerary-01-12-2025.pdf", 
        "target": "airport", 
        "provider": "shuttle"
    }
}