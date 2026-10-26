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

    # --- OSYPA (Автобусы Пафоса - 41 маршрут) ---
    "osypa_601": {
        "name": "601: Karavela Station - Geroskipou - Timi - Anarita - Mandria",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/601",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_602": {
        "name": "602: Karavela Station - Museum - Government Offices - Karavela Station",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/602",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_603": {
        "name": "603: Tombs Of The Kings Station - Universal Area - Museum - Karavela Station",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_603b": {
        "name": "603B: Tombs Of The Kings Station - Universal Area - Al. Papagou",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/603b",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_604": {
        "name": "604: Karavela Station - Emba - Tala - Agios Neofytos Monastery",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/604",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_606": {
        "name": "606: Geroskipou (Pafiako) - Geroskipou Beach - Kings Av. Mall - Harbour Station",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/606",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_607": {
        "name": "607: Karavela Station - Chloraka - Lemba - Kissonerga - Pegeia",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/607",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_608": {
        "name": "608: Karavella Station - General Hospital - Anavargos",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/608",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_609": {
        "name": "609: Karavella Station - Konia - Marathounta - Armou - Episkopi",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/609",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_610": {
        "name": "610: Municipal Market - Kato Paphos (Harbour)",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/610",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_611": {
        "name": "611: Tombs Of The Kings Station - Harbour - Geroskipou Beach (Waterpark)",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/611",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_airport": {
        "name": "612: Tombs of the Kings Bus Station - Paphos Airport",
        "url": "https://www.pafosbuses.com/pafos-airport-bus-routes-1/612",
        "target": "airport",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_airport_613": {
        "name": "613: Karavela Station - Paphos Airport",
        "url": "https://www.pafosbuses.com/pafos-airport-bus-routes-1/613",
        "target": "airport",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_614": {
        "name": "614: Karavela Station -Tremithousa - Mesogi - Mesa Xorio - Tsada- Koili",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/614",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_615": {
        "name": "615: Tombs Of The Kings Station - Coral Bay",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/615",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_616": {
        "name": "616: Coral Bay - Pegeia - Agios Georgios Pegeias",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/616",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_616b": {
        "name": "616B: Coral Bay - Agios Georgios (via Sea Caves)",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/616b",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_618": {
        "name": "618: Karavela Station - Kennedy Square - Tombs Of The Kings Station",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/618",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_621": {
        "name": "621: Polis Bus Station - Polis Hospital",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/621",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_622": {
        "name": "622: Polis Chrysochous - Baths of Aphrodite",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/622",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_623": {
        "name": "623: Polis Chrysochous - Neo Chorio",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/623",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_624": {
        "name": "624: Pelathousa - Polis Chrysochous",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/624",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_625": {
        "name": "625: Kinousa - Polis Chrysochous",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/625",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_630": {
        "name": "630: Karavela - Geroskipou - Acheleia - Timi - Kouklia - Petra tou Romiou - Pissouri",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/630",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_631": {
        "name": "631: Harbour Station - Petra tou Romiou",
        "url": "https://www.pafosbuses.com/pafos-city-suburbs-routes-1/631",
        "target": "city",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_632": {
        "name": "632: Paphos (Karavela Station) - Archimandrita",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/632",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_633": {
        "name": "633: Paphos (Karavela Station) - Agios Nikolaos",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/633",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_634": {
        "name": "634: Paphos (Karavela Station) - Arminou",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/634",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_635": {
        "name": "635: Agios Ioannis - Stavrokonnou",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/635",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_636": {
        "name": "636: Paphos (Karavela) - Statos / Agios Fotios",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/636",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_637": {
        "name": "637: Paphos (Karavela Station) - Panagia",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/637",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_638": {
        "name": "638: Milia - Agios Demetrianos (Circular)",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/638",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_639": {
        "name": "639: Choulou - Paphos (Karavela)",
        "url": "https://www.pafosbuses.com/pafos-villages-bus-routes-1/639",
        "target": "villages",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_640": {
        "name": "640: Lysos - Polis Chrysochous",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/640",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_641": {
        "name": "641: Polis - Terra - Droushia - Inia - Kathikas - Theletra - Paphos",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/641",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_643a": {
        "name": "643A: Pachyammos - Polis Chrysochous",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/643a",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_643b": {
        "name": "643B: Pachyammos - Pano Argaka - Polis Chrysochous",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/643b",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_645": {
        "name": "645: Polis Chrysochous - Paphos (Karavela)",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/645",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_646": {
        "name": "646: Polis Chrysochous - Miliou - Giolou",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/646",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_647": {
        "name": "647: Polis Chrysochous - Androlykou",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/647",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
    },
    "osypa_648": {
        "name": "648: Polis Chrysochous - Droushia - Inia - Arodes - Kathikas - Peyia - Coral Bay",
        "url": "https://www.pafosbuses.com/polis-latchi-bus-routes-1/648",
        "target": "polis",
        "provider": "osypa",
        "duration": "~ 30m"
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