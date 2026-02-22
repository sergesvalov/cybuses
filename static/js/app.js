import { Api } from './api.js';
import { FilterBar } from './components/FilterBar.js';
import { BusCard } from './components/BusCard.js';
import { Modal } from './components/Modal.js';

class BusApp {
    constructor() {
        this.data = [];
        this.appEl = document.getElementById('app');
        this.refreshBtn = document.getElementById('r-btn');
        this.searchInput = document.getElementById('route-search');
        this.searchQuery = '';
        this.favorites = JSON.parse(localStorage.getItem('cybuses_favs') || '[]');

        // Initialize Components
        this.modal = new Modal('modal');
        this.filterBar = new FilterBar('filter-container', (newState) => {
            this.render();
        });

        this.bindEvents();
    }

    bindEvents() {
        // Render initial filter DOM
        this.filterBar.render();

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

        // Search input logic
        this.searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase().trim();
            this.render();
        });

        // Initialize polling for time highlighting
        setInterval(() => this.highlightNext(), 60000);
    }

    getCurrentDayType() {
        // Use Cyprus timezone for accurate day calculation
        const cyprusTime = new Date().toLocaleString("en-US", { timeZone: "Asia/Nicosia" });
        const cyprusDate = new Date(cyprusTime);
        const day = cyprusDate.getDay();
        // 0 = Sunday, 6 = Saturday
        return (day === 0 || day === 6) ? 'weekend' : 'weekday';
    }

    async load() {
        this.appEl.innerHTML = '<div class="loader">Загрузка расписания...</div>';
        try {
            this.data = await Api.fetchData();
            this.render();
        } catch (e) {
            this.appEl.innerHTML = '<div class="loader">Ошибка сервера. Попробуйте обновить страницу.</div>';
            console.error(e);
        }
    }

    render() {
        this.appEl.innerHTML = '';

        const state = this.filterBar.getState();
        const activeDayType = state.d === 'auto' || state.d === 'nearest' ? this.getCurrentDayType() : state.d;

        const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const currentDayName = dayNames[new Date().getDay()];

        const fData = this.data.reduce((acc, route) => {
            // Text Search Check
            const q = this.searchQuery;
            if (q) {
                const searchStr = `${route.name} ${route.desc}`.toLowerCase();
                if (!searchStr.includes(q)) return acc;
            }

            const matchProv = (state.p === 'all' || route.prov === state.p);

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

            if (!matchProv || !matchDay) return acc;

            if (state.d === 'nearest') {
                const now = new Date();
                const curMins = now.getHours() * 60 + now.getMinutes();

                const filteredTimes = route.times.map(t => {
                    const txt = (t.t || "").replace(/[^\d:]/g, '');
                    if (!txt) return null;
                    const [h, m] = txt.split(':').map(Number);
                    let busMins = h * 60 + m;

                    let effectiveBus = busMins;
                    let effectiveCur = curMins;

                    if (effectiveBus < 180) effectiveBus += 1440;
                    if (effectiveCur < 180) effectiveCur += 1440;

                    const diff = effectiveBus - effectiveCur;
                    if (diff >= 30 && diff <= 120) {
                        return { ...t, diffMins: diff };
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

        // Sort Data: Favorites first
        fData.sort((a, b) => {
            const getFavKey = (r) => `${r.prov}_${r.name}_${r.desc}`;
            const keyA = getFavKey(a);
            const keyB = getFavKey(b);
            const favA = this.favorites.includes(keyA) ? 1 : 0;
            const favB = this.favorites.includes(keyB) ? 1 : 0;
            return favB - favA;
        });

        if (!fData.length) {
            this.appEl.innerHTML = '<div class="loader">Рейсов не найдено</div>';
            return;
        }

        fData.forEach(r => {
            const favKey = `${r.prov}_${r.name}_${r.desc}`;
            r.isFav = this.favorites.includes(favKey);

            const cardComponent = new BusCard(r, (time, stars, note) => {
                this.modal.show(time, stars, note);
            });

            this.appEl.appendChild(cardComponent.render());
        });

        // Compute highlighting strictly after DOM insertion
        this.highlightNext();
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
                this.render(); // Re-render to apply sort and icon changes
            });
        });
    }

    highlightNext() {
        const now = new Date();
        const curMins = now.getHours() * 60 + now.getMinutes();

        document.querySelectorAll('.card').forEach(card => {
            let foundNext = false;
            card.querySelectorAll('.t-btn').forEach(btn => {
                const innerT = btn.childNodes[0].nodeValue || "";
                const txt = innerT.replace(/[^\d:]/g, '');
                if (!txt || txt.length < 4) return;

                const [h, m] = txt.split(':').map(Number);
                let busMins = h * 60 + m;

                let effectiveBus = busMins;
                let effectiveCur = curMins;

                // Shift night buses to the next logical day segment
                if (effectiveBus < 180) effectiveBus += 1440;
                if (effectiveCur < 180) effectiveCur += 1440;

                btn.classList.remove('past', 'next');
                if (effectiveBus < effectiveCur) {
                    btn.classList.add('past');
                } else if (!foundNext) {
                    btn.classList.add('next');
                    foundNext = true;
                }
            });
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
