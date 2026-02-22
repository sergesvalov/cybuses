import { Api } from './api.js';
import { FilterBar } from './components/FilterBar.js';
import { BusCard } from './components/BusCard.js';
import { Modal } from './components/Modal.js';

class BusApp {
    constructor() {
        this.data = [];
        this.appEl = document.getElementById('app');
        this.refreshBtn = document.getElementById('r-btn');

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
        this.refreshBtn.addEventListener('click', () => {
            this.refresh();
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
            const matchProv = (state.p === 'all' || route.prov === state.p);

            let matchDay = false;
            if (route.type === 'all') {
                matchDay = true;
            } else if (['weekday', 'weekend'].includes(route.type)) {
                matchDay = (route.type === activeDayType);
            } else {
                // Route is an explicit day (e.g., 'monday')
                if (state.d === 'auto' || state.d === 'nearest') {
                    matchDay = (route.type === currentDayName);
                } else if (state.d === 'weekday') {
                    matchDay = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].includes(route.type);
                } else if (state.d === 'weekend') {
                    matchDay = ['saturday', 'sunday'].includes(route.type);
                }
            }

            if (!matchProv || !matchDay) return acc;

            if (state.d === 'nearest') {
                const now = new Date();
                const curMins = now.getHours() * 60 + now.getMinutes();

                const filteredTimes = route.times.filter(t => {
                    const txt = (t.t || "").replace(/[^\d:]/g, '');
                    if (!txt) return false;
                    const [h, m] = txt.split(':').map(Number);
                    let busMins = h * 60 + m;

                    let effectiveBus = busMins;
                    let effectiveCur = curMins;

                    if (effectiveBus < 180) effectiveBus += 1440;
                    if (effectiveCur < 180) effectiveCur += 1440;

                    const diff = effectiveBus - effectiveCur;
                    return diff >= 30 && diff <= 120;
                });

                if (filteredTimes.length > 0) {
                    acc.push({ ...route, times: filteredTimes });
                }
            } else {
                acc.push(route);
            }
            return acc;
        }, []);

        if (!fData.length) {
            this.appEl.innerHTML = '<div class="loader">Рейсов не найдено</div>';
            return;
        }

        fData.forEach(r => {
            const cardComponent = new BusCard(r, (time, stars, note) => {
                this.modal.show(time, stars, note);
            });

            this.appEl.appendChild(cardComponent.render());
        });

        // Compute highlighting strictly after DOM insertion
        this.highlightNext();
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
