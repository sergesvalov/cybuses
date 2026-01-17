# Настройка маршрутов
# provider: указывает, какой файл из папки parsers использовать

ROUTES = {
    # INTERCITY
    "limassol": {"name": "Лимассол", "url": "https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/", "target": "limassol", "provider": "intercity"},
    "nicosia": {"name": "Никосия", "url": "https://intercity-buses.com/en/routes/nicosia-paphos-paphos-nicosia/", "target": "nicosia", "provider": "intercity"},
    "larnaca": {"name": "Ларнака", "url": "https://intercity-buses.com/en/routes/larnaca-paphos-paphos-larnaca/", "target": "larnaca", "provider": "intercity"},
    
    # OSYPA (ГОРОДСКИЕ ПАФОСА)
    "osypa_618": {"name": "618: Harbour - Karavella", "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/618", "target": "city", "provider": "osypa"},
    "osypa_603": {"name": "603: Harbour - Karavella", "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603", "target": "city", "provider": "osypa"},
    "osypa_603B": {"name": "603B: Harbour - Karavella", "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603b", "target": "city", "provider": "osypa"},
    
    # АЭРОПОРТЫ
    "kapnos": {"name": "Kapnos (Larnaca)", "url": "https://kapnosairportshuttle.com/timetables", "target": "airport", "provider": "shuttle"},
    "express": {"name": "Express (Limassol)", "url": "https://limassolairportexpress.eu/?page_id=280", "target": "airport", "provider": "shuttle"}
}