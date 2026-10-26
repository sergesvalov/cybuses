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
