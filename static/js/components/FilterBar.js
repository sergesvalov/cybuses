import { t } from '../i18n.js';

export class FilterBar {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        this.state = {
            c: 'all', // city
            p: 'all', // provider or 'favorites'
            d: 'auto' // day type
        };
    }

    render() {
        const isActive = (filter, val) => this.state[filter] === val ? 'active' : '';

        this.container.innerHTML = `
            <div class="filter-group">
                <div class="f-label">${t('city')}</div>
                <div class="scroll-row" id="city-filters">
                    <button class="pill-btn ${isActive('c', 'all')}" data-filter="c" data-val="all">${t('all')}</button>
                    <button class="pill-btn ${isActive('c', 'paphos')}" data-filter="c" data-val="paphos">${t('paphos')}</button>
                    <button class="pill-btn ${isActive('c', 'limassol')}" data-filter="c" data-val="limassol">${t('limassol')}</button>
                    <button class="pill-btn ${isActive('c', 'nicosia')}" data-filter="c" data-val="nicosia">${t('nicosia')}</button>
                    <button class="pill-btn ${isActive('c', 'larnaca')}" data-filter="c" data-val="larnaca">${t('larnaca')}</button>
                    <button class="pill-btn ${isActive('c', 'paralimni')}" data-filter="c" data-val="paralimni">${t('paralimni')}</button>
                </div>
            </div>

            <div class="filter-group">
                <div class="f-label">${t('agency')}</div>
                <div class="scroll-row" id="agency-filters">
                    <button class="pill-btn ${isActive('p', 'all')}" data-filter="p" data-val="all">${t('all')}</button>
                    <button class="pill-btn fav-pill ${isActive('p', 'favorites')}" data-filter="p" data-val="favorites">${t('favoritesOnly')}</button>
                    <button class="pill-btn ${isActive('p', 'intercity')}" data-filter="p" data-val="intercity">Intercity</button>
                    <button class="pill-btn ${isActive('p', 'osypa')}" data-filter="p" data-val="osypa">City (Osypa)</button>
                    <button class="pill-btn ${isActive('p', 'shuttle')}" data-filter="p" data-val="shuttle">Airport</button>
                    <button class="pill-btn ${isActive('p', 'manual')}" data-filter="p" data-val="manual">Custom</button>
                </div>
            </div>

            <div class="filter-group">
                <div class="f-label">${t('dayTime')}</div>
                <div class="scroll-row" id="day-filters">
                    <button class="pill-btn ${isActive('d', 'auto')}" data-filter="d" data-val="auto">${t('auto')}</button>
                    <button class="pill-btn ${isActive('d', 'weekday')}" data-filter="d" data-val="weekday">${t('weekdays')}</button>
                    <button class="pill-btn ${isActive('d', 'weekend')}" data-filter="d" data-val="weekend">${t('weekends')}</button>
                    <button class="pill-btn ${isActive('d', 'nearest')}" data-filter="d" data-val="nearest">${t('nearest')}</button>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const buttons = this.container.querySelectorAll('.pill-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.currentTarget;
                const filterKey = target.getAttribute('data-filter');
                const filterVal = target.getAttribute('data-val');

                // Update local state
                this.state[filterKey] = filterVal;

                // Update UI state
                target.parentElement.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
                target.classList.add('active');

                this.onFilterChange(this.state);
            });
        });
    }

    getState() {
        return this.state;
    }
}
