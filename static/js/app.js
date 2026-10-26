import { Api } from './api.js?v=11';
import { FilterBar } from './components/FilterBar.js?v=11';
import { RouteFinder } from './components/RouteFinder.js?v=11';
import { BusCard } from './components/BusCard.js?v=11';
import { JourneyPlanner } from './components/JourneyPlanner.js?v=11';
import { Modal } from './components/Modal.js?v=11';
import { t, getLang, setLang } from './i18n.js?v=11';

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

        // Tab Navigation Elements
        this.activeTab = localStorage.getItem('cybuses_active_tab') || 'search';
        this.tabBtnSearch = document.getElementById('tab-btn-search');
        this.tabBtnCatalog = document.getElementById('tab-btn-catalog');
        this.viewSearch = document.getElementById('view-search');
        this.viewCatalog = document.getElementById('view-catalog');
        this.tabLabelSearch = document.getElementById('tab-label-search');
        this.tabLabelCatalog = document.getElementById('tab-label-catalog');

        // Initialize Components
        this.modal = new Modal('modal');
        this.routeFinder = new RouteFinder('route-finder-container', () => {
            if (this.activeTab === 'search') this.render();
        });
        this.filterBar = new FilterBar('filter-container', () => {
            if (this.activeTab === 'catalog') this.render();
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
            this.langBtn.textContent = getLang().toUpperCase();
            this.langBtn.setAttribute('title', getLang() === 'ru' ? 'Switch to English' : 'Переключить на русский');
        }
    }

    updateTexts() {
        if (this.tabLabelSearch) {
            this.tabLabelSearch.textContent = t('tabSearch');
        }
        if (this.tabLabelCatalog) {
            this.tabLabelCatalog.textContent = t('tabCatalog');
        }
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

    switchTab(tab) {
        this.activeTab = tab;
        localStorage.setItem('cybuses_active_tab', tab);

        const isSearch = tab === 'search';
        if (this.tabBtnSearch) {
            this.tabBtnSearch.classList.toggle('active', isSearch);
            this.tabBtnSearch.setAttribute('aria-selected', isSearch ? 'true' : 'false');
        }
        if (this.tabBtnCatalog) {
            this.tabBtnCatalog.classList.toggle('active', !isSearch);
            this.tabBtnCatalog.setAttribute('aria-selected', !isSearch ? 'true' : 'false');
        }

        if (this.viewSearch) {
            this.viewSearch.style.display = isSearch ? 'block' : 'none';
        }
        if (this.viewCatalog) {
            this.viewCatalog.style.display = !isSearch ? 'block' : 'none';
        }

        this.render();
    }

    bindEvents() {
        this.updateLangButton();
        this.updateTexts();

        // Render initial UI components
        this.routeFinder.render();
        this.filterBar.render();

        // Initialize active tab visibility
        this.switchTab(this.activeTab);

        // Tab click listeners
        if (this.tabBtnSearch) {
            this.tabBtnSearch.addEventListener('click', () => this.switchTab('search'));
        }
        if (this.tabBtnCatalog) {
            this.tabBtnCatalog.addEventListener('click', () => this.switchTab('catalog'));
        }

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

        // Search input logic with debounce (Tab 1)
        const debouncedSearch = debounce((query) => {
            this.searchQuery = query;
            if (this.activeTab === 'search') this.render();
        }, 150);

        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                debouncedSearch(e.target.value.toLowerCase().trim());
            });
        }

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
            console.error("Failed to load or render data:", e);
        }
    }

    render() {
        this.appEl.innerHTML = '';

        if (this.activeTab === 'search') {
            this.renderSearchTab();
        } else {
            this.renderCatalogTab();
        }
    }

    renderSearchTab() {
        const activeDayType = this.getCurrentDayType();
        const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        const weekends = ['saturday', 'sunday'];
        const curMins = this.getCyprusMinutes();
        const rfState = this.routeFinder.getState();

        const isOriginDestSelected = rfState.from !== 'any' && rfState.to !== 'any' && rfState.from !== rfState.to;

        // 1. If Origin and Destination are selected, compute Journey Itineraries (including transfers)
        let itineraries = [];
        if (isOriginDestSelected) {
            itineraries = JourneyPlanner.planJourney(this.data, rfState.from, rfState.to, {
                curMins,
                dayType: activeDayType
            });
        }

        // 2. Direct route cards matching
        const fData = this.data.reduce((acc, route) => {
            // Direct RouteFinder match (Origin -> Destination)
            if (!this.routeFinder.matchRoute(route)) {
                return acc;
            }

            // Text Search Query Check
            if (this.searchQuery) {
                const searchStr = `${route.name} ${route.desc}`.toLowerCase();
                if (!searchStr.includes(this.searchQuery)) return acc;
            }

            // Current day schedule match (auto)
            let matchDay = false;
            if (route.type === 'all') {
                matchDay = true;
            } else if (activeDayType === 'weekday') {
                matchDay = (route.type === 'weekday' || weekdays.includes(route.type));
            } else if (activeDayType === 'weekend') {
                matchDay = (route.type === 'weekend' || weekends.includes(route.type));
            }

            if (matchDay) {
                acc.push(route);
            }
            return acc;
        }, []);

        // Sort Favorites first
        fData.sort((a, b) => {
            const getFavKey = (r) => `${r.prov}_${r.name}_${r.desc}`;
            const favA = this.favorites.includes(getFavKey(a)) ? 1 : 0;
            const favB = this.favorites.includes(getFavKey(b)) ? 1 : 0;
            return favB - favA;
        });

        // If itineraries with transfers exist, render them prominently!
        if (itineraries.length > 0) {
            const itSection = document.createElement('div');
            itSection.className = 'itinerary-section';
            itSection.innerHTML = `<h3 class="itinerary-section-title">🧭 ${t('connectionsAvailable')}</h3>`;

            itineraries.forEach(it => {
                itSection.appendChild(JourneyPlanner.renderItineraryCard(it));
            });

            this.appEl.appendChild(itSection);

            // Also render direct timetable cards if any exist
            if (fData.length > 0) {
                const directTitle = document.createElement('h3');
                directTitle.className = 'itinerary-section-title';
                directTitle.style.marginTop = '24px';
                directTitle.textContent = `📋 ${t('directRoutes')}`;
                this.appEl.appendChild(directTitle);
                this.renderCardList(fData);
            }
            return;
        }

        // If no itineraries and no direct routes
        if (!fData.length) {
            if (rfState.from !== 'any' || rfState.to !== 'any') {
                this.appEl.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🎯</div>
                        <div class="empty-text">${t('noDirectRoutes')}</div>
                    </div>`;
            } else if (this.searchQuery) {
                this.appEl.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🔍</div>
                        <div class="empty-text">${t('noRoutes')}</div>
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

        this.renderCardList(fData);
    }

    renderCatalogTab() {
        const state = this.filterBar.getState();
        const activeDayType = state.d === 'auto' || state.d === 'nearest' ? this.getCurrentDayType() : state.d;

        const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        const weekends = ['saturday', 'sunday'];
        const todayDayType = this.getCurrentDayType();
        const curMins = this.getCyprusMinutes();

        const fData = this.data.reduce((acc, route) => {
            const favKey = `${route.prov}_${route.name}_${route.desc}`;
            const isFav = this.favorites.includes(favKey);

            // 1. Agency filter (state.p)
            if (state.p === 'favorites') {
                if (!isFav) return acc;
            } else if (state.p !== 'all' && route.prov !== state.p) {
                return acc;
            }

            // 2. Routes / Categories / Cities filter
            const nameLower = (route.name || '').toLowerCase();
            const descLower = (route.desc || '').toLowerCase();
            const combined = `${nameLower} ${descLower}`;

            if (state.p === 'osypa' && state.r !== 'all') {
                const matchRouteNum = nameLower.match(/^\s*(\d+[a-z]?)/i);
                const num = matchRouteNum ? matchRouteNum[1].toUpperCase() : '';

                if (state.r === 'airport') {
                    if (num !== '612' && num !== '613') return acc;
                } else if (state.r === 'villages') {
                    const villageNums = ['630', '632', '633', '634', '635', '636', '637', '638', '639'];
                    if (!villageNums.includes(num)) return acc;
                } else if (state.r === 'polis') {
                    const polisNums = ['621', '622', '623', '624', '625', '640', '641', '643A', '643B', '645', '646', '647', '648'];
                    if (!polisNums.includes(num)) return acc;
                } else if (state.r === 'city') {
                    const cityNums = ['601', '602', '603', '603B', '604', '606', '607', '608', '609', '610', '611', '614', '615', '616', '616B', '618', '631'];
                    if (!cityNums.includes(num)) return acc;
                }
            } else if (state.p === 'intercity' && state.r !== 'all') {
                if (state.r === 'paphos_limassol') {
                    if (!combined.includes('paphos') || !combined.includes('limassol')) return acc;
                } else if (state.r === 'paphos_nicosia') {
                    if (!combined.includes('paphos') || !combined.includes('nicosia')) return acc;
                } else if (state.r === 'limassol_nicosia') {
                    if (!combined.includes('limassol') || !combined.includes('nicosia')) return acc;
                } else if (state.r === 'limassol_larnaca') {
                    if (!combined.includes('limassol') || !combined.includes('larnaca')) return acc;
                } else if (state.r === 'larnaca_nicosia') {
                    if (!combined.includes('larnaca') || !combined.includes('nicosia')) return acc;
                } else if (state.r === 'paralimni') {
                    if (!combined.includes('paralimni') && !combined.includes('ayia napa') && !combined.includes('famagusta')) return acc;
                }
            } else if (state.p === 'shuttle' && state.r !== 'all') {
                if (state.r === 'kapnos' && !combined.includes('kapnos')) return acc;
                if (state.r === 'limassol_express' && !combined.includes('limassol airport express')) return acc;
            } else if ((state.p === 'all' || state.p === 'favorites') && state.c !== 'all') {
                const c = state.c.toLowerCase();
                let matchCity = combined.includes(c);
                if (c === 'paphos' && (route.prov === 'osypa' || combined.includes('pfo') || combined.includes('пафос'))) matchCity = true;
                if (c === 'larnaca' && (combined.includes('kapnos') || combined.includes('lca') || combined.includes('ларнака'))) matchCity = true;
                if (c === 'limassol' && (combined.includes('limassol airport express') || combined.includes('лимассол'))) matchCity = true;
                if (c === 'polis' && (combined.includes('polis') || combined.includes('latchi') || combined.includes('полис') || combined.includes('лачи'))) matchCity = true;
                if (!matchCity) return acc;
            }

            // 3. Day match
            let matchDay = false;
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

            if (!matchDay) return acc;

            // Nearest filter
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

        // Sort Favorites first
        fData.sort((a, b) => {
            const getFavKey = (r) => `${r.prov}_${r.name}_${r.desc}`;
            const favA = this.favorites.includes(getFavKey(a)) ? 1 : 0;
            const favB = this.favorites.includes(getFavKey(b)) ? 1 : 0;
            return favB - favA;
        });

        if (!fData.length) {
            if (state.p === 'favorites') {
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

    renderCardList(routesList) {
        const frag = document.createDocumentFragment();
        const isToday = true;
        const curMins = this.getCyprusMinutes();

        routesList.forEach(r => {
            const favKey = `${r.prov}_${r.name}_${r.desc}`;
            r.isFav = this.favorites.includes(favKey);

            const cardComponent = new BusCard(r, (time, stars, note) => {
                this.modal.show(time, stars, note);
            }, {
                isToday,
                curMins
            });

            frag.appendChild(cardComponent.render());
        });

        this.appEl.appendChild(frag);
        this.bindCardEvents();
        this.highlightNext();
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
        const todayDayType = this.getCurrentDayType();
        let isToday = true;
        if (this.activeTab === 'catalog') {
            const state = this.filterBar.getState();
            const activeDayType = state.d === 'auto' || state.d === 'nearest' ? todayDayType : state.d;
            isToday = (activeDayType === todayDayType || state.d === 'auto' || state.d === 'nearest');
        }

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
}

// Start application on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new BusApp();
    app.load();
});
