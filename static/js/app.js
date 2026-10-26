import { Api } from './api.js';
import { FilterBar } from './components/FilterBar.js';
import { RouteFinder } from './components/RouteFinder.js';
import { BusCard } from './components/BusCard.js';
import { Modal } from './components/Modal.js';
import { t, getLang, setLang } from './i18n.js';

class BusApp {
    constructor() {
        this.data = [];
        this.appEl = document.getElementById('app');
        this.refreshBtn = document.getElementById('r-btn');
        this.langBtn = document.getElementById('lang-btn');
        this.searchInput = document.getElementById('route-search');
        this.updateTimeEl = document.getElementById('update-time');
        this.offlineBadge = document.getElementById('offline-badge');
        this.searchQuery = '';
        this.favorites = JSON.parse(localStorage.getItem('cybuses_favs') || '[]');

        // Initialize Components
        this.modal = new Modal('modal');
        this.routeFinder = new RouteFinder('route-finder-container', () => {
            this.render();
        });
        this.filterBar = new FilterBar('filter-container', () => {
            this.render();
        });

        this.bindEvents();
    }

    getCyprusDate() {
        const cyprusTime = new Date().toLocaleString("en-US", { timeZone: "Asia/Nicosia" });
        return new Date(cyprusTime);
    }

    getCurrentDayType() {
        const day = this.getCyprusDate().getDay();
        // 0 = Sunday, 6 = Saturday
        return (day === 0 || day === 6) ? 'weekend' : 'weekday';
    }

    getCyprusMinutes() {
        const cd = this.getCyprusDate();
        return cd.getHours() * 60 + cd.getMinutes();
    }

    updateLangButton() {
        if (this.langBtn) {
            // Show current language badge
            this.langBtn.textContent = getLang().toUpperCase();
            this.langBtn.setAttribute('title', getLang() === 'ru' ? 'Switch to English' : 'Переключить на русский');
        }
    }

    updateTexts() {
        if (this.searchInput) {
            this.searchInput.placeholder = t('searchPlaceholder');
        }
        const mClose = document.getElementById('m-close');
        if (mClose) {
            mClose.textContent = t('modalGotIt');
        }
        this.updateStatusTime();
        this.updateOnlineStatus();
    }

    updateOnlineStatus() {
        if (this.offlineBadge) {
            this.offlineBadge.style.display = navigator.onLine ? 'none' : 'inline-block';
            this.offlineBadge.textContent = `⚡ ${t('offline')}`;
        }
    }

    updateStatusTime() {
        if (!this.updateTimeEl) return;
        const pad = (n) => String(n).padStart(2, '0');

        if (Api.lastUpdated) {
            try {
                const d = new Date(Api.lastUpdated);
                const timeStr = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
                this.updateTimeEl.textContent = `🕒 ${t('updatedAt', { time: timeStr })}`;
                return;
            } catch (e) {
                // fallback below
            }
        }

        const cd = this.getCyprusDate();
        const timeStr = `${pad(cd.getHours())}:${pad(cd.getMinutes())}`;
        this.updateTimeEl.textContent = `🕒 ${t('updatedAt', { time: timeStr })}`;
    }

    bindEvents() {
        this.updateLangButton();
        this.updateTexts();

        // Render initial UI components
        this.routeFinder.render();
        this.filterBar.render();

        // Language toggle
        if (this.langBtn) {
            this.langBtn.addEventListener('click', () => {
                const next = getLang() === 'ru' ? 'en' : 'ru';
                setLang(next);
                this.updateLangButton();
                this.updateTexts();
                this.routeFinder.render();
                this.filterBar.render();
                this.render();
            });
        }

        // Online/Offline status listeners
        window.addEventListener('online', () => this.updateOnlineStatus());
        window.addEventListener('offline', () => this.updateOnlineStatus());

        // Refresh button logic
        this.refreshBtn.addEventListener('click', async () => {
            this.refreshBtn.classList.add('loading');
            try {
                await Api.refreshData();
                await this.load();
            } catch (e) {
                console.error("Refresh failed", e);
            } finally {
                this.refreshBtn.classList.remove('loading');
            }
        });

        // Debounce helper
        const debounce = (fn, delay = 150) => {
            let timer;
            return (...args) => {
                clearTimeout(timer);
                timer = setTimeout(() => fn.apply(this, args), delay);
            };
        };

        // Search input logic with debounce
        const debouncedSearch = debounce((query) => {
            this.searchQuery = query;
            this.render();
        }, 150);

        this.searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value.toLowerCase().trim());
        });

        // Polling for live countdown and highlighting (every 30s)
        setInterval(() => this.highlightNext(), 30000);
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.highlightNext();
            }
        });
    }

    async load() {
        this.appEl.innerHTML = `<div class="loader">${t('loading')}</div>`;
        try {
            this.data = await Api.fetchData();
            this.updateStatusTime();
            this.render();
        } catch (e) {
            this.appEl.innerHTML = `<div class="loader">${t('serverError')}</div>`;
            console.error(e);
        }
    }

    render() {
        this.appEl.innerHTML = '';

        const state = this.filterBar.getState();
        const activeDayType = state.d === 'auto' || state.d === 'nearest' ? this.getCurrentDayType() : state.d;

        const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const todayDayType = this.getCurrentDayType();
        const curMins = this.getCyprusMinutes();

        const fData = this.data.reduce((acc, route) => {
            const favKey = `${route.prov}_${route.name}_${route.desc}`;
            const isFav = this.favorites.includes(favKey);

            // RouteFinder (Origin -> Destination) Check
            if (!this.routeFinder.matchRoute(route)) {
                return acc;
            }

            // Favorites filter check
            if (state.p === 'favorites') {
                if (!isFav) return acc;
            } else if (state.p !== 'all' && route.prov !== state.p) {
                return acc;
            }

            // Text Search Check
            const q = this.searchQuery;
            if (q) {
                const searchStr = `${route.name} ${route.desc}`.toLowerCase();
                if (!searchStr.includes(q)) return acc;
            }

            let matchCity = true;
            if (state.c && state.c !== 'all') {
                const c = state.c.toLowerCase();
                const searchStr = `${route.name} ${route.desc}`.toLowerCase();
                matchCity = searchStr.includes(c);
                if (c === 'paphos' && (route.prov === 'osypa' || route.prov === 'shuttle')) matchCity = true;
                if (c === 'larnaca' && route.name.toLowerCase().includes('kapnos')) matchCity = true;
                if (c === 'limassol' && route.name.toLowerCase().includes('limassol airport express')) matchCity = true;
            }

            let matchDay = false;
            const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
            const weekends = ['saturday', 'sunday'];

            if (route.type === 'all') {
                matchDay = true;
            } else {
                if (activeDayType === 'weekday') {
                    matchDay = (route.type === 'weekday' || weekdays.includes(route.type));
                } else if (activeDayType === 'weekend') {
                    matchDay = (route.type === 'weekend' || weekends.includes(route.type));
                } else if (dayNames.includes(activeDayType)) {
                    if (route.type === activeDayType) {
                        matchDay = true;
                    } else if (route.type === 'weekday' && weekdays.includes(activeDayType)) {
                        matchDay = true;
                    } else if (route.type === 'weekend' && weekends.includes(activeDayType)) {
                        matchDay = true;
                    }
                }
            }

            if (!matchDay || !matchCity) return acc;

            if (state.d === 'nearest') {
                const filteredTimes = route.times.map(tObj => {
                    const txt = (tObj.t || "").replace(/[^\d:]/g, '');
                    if (!txt) return null;
                    const [h, m] = txt.split(':').map(Number);
                    let busMins = h * 60 + m;

                    let effectiveBus = busMins;
                    let effectiveCur = curMins;

                    if (effectiveBus < 180) effectiveBus += 1440;
                    if (effectiveCur < 180) effectiveCur += 1440;

                    const diff = effectiveBus - effectiveCur;
                    if (diff >= 0 && diff <= 120) {
                        return { ...tObj, diffMins: diff };
                    }
                    return null;
                }).filter(Boolean);

                if (filteredTimes.length > 0) {
                    acc.push({ ...route, times: filteredTimes });
                }
            } else {
                acc.push(route);
            }
            return acc;
        }, []);

        // Sort Data: Favorites first (unless already filtering by favorites)
        fData.sort((a, b) => {
            const getFavKey = (r) => `${r.prov}_${r.name}_${r.desc}`;
            const favA = this.favorites.includes(getFavKey(a)) ? 1 : 0;
            const favB = this.favorites.includes(getFavKey(b)) ? 1 : 0;
            return favB - favA;
        });

        if (!fData.length) {
            const rfState = this.routeFinder.getState();
            if (rfState.from !== 'any' || rfState.to !== 'any') {
                this.appEl.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🎯</div>
                        <div class="empty-text">${t('noDirectRoutes')}</div>
                    </div>`;
            } else if (state.p === 'favorites') {
                this.appEl.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">⭐</div>
                        <div class="empty-text">${t('noFavorites')}</div>
                    </div>`;
            } else {
                this.appEl.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🚌</div>
                        <div class="empty-text">${t('noRoutes')}</div>
                    </div>`;
            }
            return;
        }

        // Determine whether active day filter represents today
        const isToday = (activeDayType === todayDayType || state.d === 'auto' || state.d === 'nearest');

        fData.forEach(r => {
            const favKey = `${r.prov}_${r.name}_${r.desc}`;
            r.isFav = this.favorites.includes(favKey);

            const cardComponent = new BusCard(r, (time, stars, note) => {
                this.modal.show(time, stars, note);
            }, {
                isToday,
                curMins
            });

            this.appEl.appendChild(cardComponent.render());
        });

        this.bindCardEvents();
    }

    bindCardEvents() {
        this.appEl.querySelectorAll('.fav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const key = btn.dataset.key;
                if (this.favorites.includes(key)) {
                    this.favorites = this.favorites.filter(k => k !== key);
                } else {
                    this.favorites.push(key);
                }
                localStorage.setItem('cybuses_favs', JSON.stringify(this.favorites));
                this.render();
            });
        });
    }

    highlightNext() {
        if (document.hidden) return;
        const curMins = this.getCyprusMinutes();
        const state = this.filterBar.getState();
        const activeDayType = state.d === 'auto' || state.d === 'nearest' ? this.getCurrentDayType() : state.d;
        const todayDayType = this.getCurrentDayType();
        const isToday = (activeDayType === todayDayType || state.d === 'auto' || state.d === 'nearest');

        if (!isToday) return;

        document.querySelectorAll('.card').forEach(card => {
            let foundNext = false;
            let nextDep = null;

            const timeWraps = card.querySelectorAll('.time-wrap');
            timeWraps.forEach(wrap => {
                const btn = wrap.querySelector('.t-btn');
                if (!btn) return;
                const txt = btn.dataset.time;
                if (!txt || txt.length < 4 || !txt.includes(':')) return;

                const [h, m] = txt.split(':').map(Number);
                let busMins = h * 60 + m;

                let effectiveBus = busMins;
                let effectiveCur = curMins;

                if (effectiveBus < 180) effectiveBus += 1440;
                if (effectiveCur < 180) effectiveCur += 1440;

                btn.classList.remove('past', 'next');
                const diff = effectiveBus - effectiveCur;

                // Remove existing live diff span
                let diffSpan = wrap.querySelector('.live-diff');

                if (diff < 0) {
                    btn.classList.add('past');
                    if (diffSpan) diffSpan.remove();
                } else if (!foundNext) {
                    btn.classList.add('next');
                    foundNext = true;
                    nextDep = { time: txt, diff };

                    const countdownText = BusCard.formatCountdown(diff);
                    if (!diffSpan) {
                        diffSpan = document.createElement('span');
                        diffSpan.className = 'live-diff';
                        wrap.appendChild(diffSpan);
                    }
                    diffSpan.textContent = countdownText;
                } else {
                    if (diffSpan) diffSpan.remove();
                }
            });

            // Update next-chip in card header
            let nextChip = card.querySelector('.next-chip');
            if (nextDep) {
                const countdownText = BusCard.formatCountdown(nextDep.diff);
                if (!nextChip) {
                    const titleRow = card.querySelector('.c-title-row');
                    if (titleRow) {
                        nextChip = document.createElement('span');
                        nextChip.className = 'next-chip';
                        titleRow.appendChild(nextChip);
                    }
                }
                if (nextChip) {
                    nextChip.innerHTML = `⚡ ${t('nextDeparture')}: <b>${nextDep.time}</b> (${countdownText})`;
                }
            } else if (nextChip) {
                nextChip.remove();
            }
        });
    }

    async refresh() {
        if (this.refreshBtn.classList.contains('spinning')) return;
        this.refreshBtn.classList.add('spinning');
        await Api.refreshData();
        this.refreshBtn.classList.remove('spinning');
        this.load();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new BusApp();
    app.load();
});
