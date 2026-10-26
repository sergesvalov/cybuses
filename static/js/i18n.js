/**
 * i18n (Internationalization) support for Cyprus Buses
 */

export const translations = {
    ru: {
        appTitle: "Cyprus Buses",
        searchPlaceholder: "Поиск по направлению (например, Аэропорт, Coral Bay)...",
        city: "Город",
        agency: "Агентство",
        dayTime: "День недели / Время",
        all: "Все",
        favoritesOnly: "⭐ Избранное",
        paphos: "Пафос",
        limassol: "Лимассол",
        nicosia: "Никосия",
        larnaca: "Ларнака",
        paralimni: "Паралимни / Айя-Напа",
        polis: "Полис / Лачи",
        auto: "Авто",
        weekdays: "Будни",
        weekends: "Выходные",
        nearest: "Ближайшие",
        loading: "Загрузка расписания...",
        noRoutes: "Рейсов не найдено",
        noFavorites: "В избранном пока ничего нет. Нажмите на звёздочку ★ на любой карточке, чтобы добавить маршрут сюда.",
        serverError: "Ошибка сервера. Попробуйте обновить страницу.",
        inMin: "через {m} мин",
        inHours: "через {h} ч {m} мин",
        now: "сейчас",
        nextDeparture: "Следующий",
        travelTime: "В пути",
        price: "Цена",
        updatedAt: "Обновлено: {time}",
        offline: "Офлайн-режим",
        refresh: "Обновить данные",
        admin: "Админ-панель",
        modalGotIt: "Понятно",
        fromCity: "Откуда",
        toCity: "Куда",
        anyCity: "Любой город / аэропорт",
        paphosAirport: "Аэропорт Пафос (PFO)",
        larnacaAirport: "Аэропорт Ларнака (LCA)",
        swap: "Поменять местами",
        reset: "Сбросить",
        directRoutes: "Прямые рейсы",
        tabSearch: "Поиск рейса",
        tabCatalog: "Маршруты и агентства",
        routeCategory: "Маршруты",
        allRoutes: "Все",
        allCities: "Все города",
        allShuttles: "Все шаттлы",
        paphosCity: "Город Пафос",
        airportLines: "Аэропорт (612, 613)",
        villages: "Деревни Пафоса",
        polisLatchi: "Полис и Лачи",
        paphosLimassol: "Пафос ↔ Лимассол",
        paphosNicosia: "Пафос ↔ Никосия",
        limassolNicosia: "Лимассол ↔ Никосия",
        limassolLarnaca: "Лимассол ↔ Ларнака",
        larnacaNicosia: "Ларнака ↔ Никосия",
        paralimniCorridor: "Паралимни / Айя-Напа",
        kapnosShuttle: "Kapnos Shuttle",
        limassolExpress: "Limassol Express",
        dayBadges: {
            weekday: "Будни",
            weekend: "Сб/Вс",
            monday: "Пн",
            tuesday: "Вт",
            wednesday: "Ср",
            thursday: "Чт",
            friday: "Пт",
            saturday: "Сб",
            sunday: "Вс",
            all: ""
        }
    },
    en: {
        appTitle: "Cyprus Buses",
        searchPlaceholder: "Search routes or stops (e.g. Airport, Coral Bay)...",
        city: "City",
        agency: "Agency",
        dayTime: "Day / Time",
        all: "All",
        favoritesOnly: "⭐ Favorites",
        paphos: "Paphos",
        limassol: "Limassol",
        nicosia: "Nicosia",
        larnaca: "Larnaca",
        paralimni: "Paralimni / Ayia Napa",
        polis: "Polis / Latchi",
        auto: "Auto",
        weekdays: "Weekdays",
        weekends: "Weekends",
        nearest: "Nearest",
        loading: "Loading schedule...",
        noRoutes: "No routes found",
        noFavorites: "No favorite routes yet. Tap the star ★ on any card to save it here.",
        serverError: "Server error. Please reload the page.",
        inMin: "in {m}m",
        inHours: "in {h}h {m}m",
        now: "now",
        nextDeparture: "Next",
        travelTime: "Duration",
        price: "Price",
        updatedAt: "Updated: {time}",
        offline: "Offline mode",
        refresh: "Refresh data",
        admin: "Admin panel",
        modalGotIt: "Got it",
        fromCity: "From",
        toCity: "To",
        anyCity: "Any city / airport",
        paphosAirport: "Paphos Airport (PFO)",
        larnacaAirport: "Larnaca Airport (LCA)",
        swap: "Swap origin & destination",
        reset: "Reset",
        directRoutes: "Direct routes",
        tabSearch: "Route Search",
        tabCatalog: "Routes & Agencies",
        routeCategory: "Routes",
        allRoutes: "All",
        allCities: "All Cities",
        allShuttles: "All Shuttles",
        paphosCity: "Paphos City",
        airportLines: "Airport (612, 613)",
        villages: "Villages",
        polisLatchi: "Polis & Latchi",
        paphosLimassol: "Paphos ↔ Limassol",
        paphosNicosia: "Paphos ↔ Nicosia",
        limassolNicosia: "Limassol ↔ Nicosia",
        limassolLarnaca: "Limassol ↔ Larnaca",
        larnacaNicosia: "Larnaca ↔ Nicosia",
        paralimniCorridor: "Paralimni / Ayia Napa",
        kapnosShuttle: "Kapnos Shuttle",
        limassolExpress: "Limassol Express",
        dayBadges: {
            weekday: "Weekdays",
            weekend: "Sat/Sun",
            monday: "Mon",
            tuesday: "Tue",
            wednesday: "Wed",
            thursday: "Thu",
            friday: "Fri",
            saturday: "Sat",
            sunday: "Sun",
            all: ""
        }
    }
};

let currentLang = localStorage.getItem('cybuses_lang') || 'ru';

export function getLang() {
    return currentLang;
}

export function setLang(lang) {
    if (lang === 'ru' || lang === 'en') {
        currentLang = lang;
        localStorage.setItem('cybuses_lang', lang);
    }
}

export function t(key, params = {}) {
    const langDict = translations[currentLang] || translations.ru;
    let text = langDict[key] !== undefined ? langDict[key] : (translations.en[key] || key);

    if (typeof text === 'string') {
        for (const [k, v] of Object.entries(params)) {
            text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
        }
    }
    return text;
}
