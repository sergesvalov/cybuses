import { t } from '../i18n.js';

export class FilterBar {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        this.state = {
            p: 'all',   // provider: 'all' | 'favorites' | 'intercity' | 'osypa' | 'shuttle' | 'manual'
            r: 'all',   // route / category filter
            c: 'all',   // city filter (when p === 'all' or 'favorites')
            d: 'auto'   // day type: 'auto' | 'weekday' | 'weekend' | 'nearest'
        };
    }

    render() {
        if (!this.container) return;

        const isActive = (key, val) => this.state[key] === val ? 'active' : '';

        // Dynamic route / sub-category buttons depending on selected agency
        let routeButtonsHtml = '';
        const p = this.state.p;

        if (p === 'osypa') {
            routeButtonsHtml = `
                <div class="filter-group">
                    <div class="f-label">${t('routeCategory')}</div>
                    <div class="scroll-row" id="route-filters">
                        <button class="pill-btn ${isActive('r', 'all')}" data-filter="r" data-val="all">${t('allRoutes')}</button>
                        <button class="pill-btn ${isActive('r', 'city')}" data-filter="r" data-val="city">${t('paphosCity')}</button>
                        <button class="pill-btn ${isActive('r', 'airport')}" data-filter="r" data-val="airport">${t('airportLines')}</button>
                        <button class="pill-btn ${isActive('r', 'villages')}" data-filter="r" data-val="villages">${t('villages')}</button>
                        <button class="pill-btn ${isActive('r', 'polis')}" data-filter="r" data-val="polis">${t('polisLatchi')}</button>
                    </div>
                </div>
            `;
        } else if (p === 'intercity') {
            routeButtonsHtml = `
                <div class="filter-group">
                    <div class="f-label">${t('routeCategory')}</div>
                    <div class="scroll-row" id="route-filters">
                        <button class="pill-btn ${isActive('r', 'all')}" data-filter="r" data-val="all">${t('allRoutes')}</button>
                        <button class="pill-btn ${isActive('r', 'paphos_limassol')}" data-filter="r" data-val="paphos_limassol">${t('paphosLimassol')}</button>
                        <button class="pill-btn ${isActive('r', 'paphos_nicosia')}" data-filter="r" data-val="paphos_nicosia">${t('paphosNicosia')}</button>
                        <button class="pill-btn ${isActive('r', 'limassol_nicosia')}" data-filter="r" data-val="limassol_nicosia">${t('limassolNicosia')}</button>
                        <button class="pill-btn ${isActive('r', 'limassol_larnaca')}" data-filter="r" data-val="limassol_larnaca">${t('limassolLarnaca')}</button>
                        <button class="pill-btn ${isActive('r', 'larnaca_nicosia')}" data-filter="r" data-val="larnaca_nicosia">${t('larnacaNicosia')}</button>
                        <button class="pill-btn ${isActive('r', 'paralimni')}" data-filter="r" data-val="paralimni">${t('paralimniCorridor')}</button>
                    </div>
                </div>
            `;
        } else if (p === 'shuttle') {
            routeButtonsHtml = `
                <div class="filter-group">
                    <div class="f-label">${t('routeCategory')}</div>
                    <div class="scroll-row" id="route-filters">
                        <button class="pill-btn ${isActive('r', 'all')}" data-filter="r" data-val="all">${t('allShuttles')}</button>
                        <button class="pill-btn ${isActive('r', 'kapnos')}" data-filter="r" data-val="kapnos">${t('kapnosShuttle')}</button>
                        <button class="pill-btn ${isActive('r', 'limassol_express')}" data-filter="r" data-val="limassol_express">${t('limassolExpress')}</button>
                    </div>
                </div>
            `;
        } else {
            // All or Favorites: show City buttons
            routeButtonsHtml = `
                <div class="filter-group">
                    <div class="f-label">${t('city')}</div>
                    <div class="scroll-row" id="city-filters">
                        <button class="pill-btn ${isActive('c', 'all')}" data-filter="c" data-val="all">${t('allCities')}</button>
                        <button class="pill-btn ${isActive('c', 'paphos')}" data-filter="c" data-val="paphos">${t('paphos')}</button>
                        <button class="pill-btn ${isActive('c', 'limassol')}" data-filter="c" data-val="limassol">${t('limassol')}</button>
                        <button class="pill-btn ${isActive('c', 'nicosia')}" data-filter="c" data-val="nicosia">${t('nicosia')}</button>
                        <button class="pill-btn ${isActive('c', 'larnaca')}" data-filter="c" data-val="larnaca">${t('larnaca')}</button>
                        <button class="pill-btn ${isActive('c', 'paralimni')}" data-filter="c" data-val="paralimni">${t('paralimni')}</button>
                        <button class="pill-btn ${isActive('c', 'polis')}" data-filter="c" data-val="polis">${t('polis')}</button>
                    </div>
                </div>
            `;
        }

        this.container.innerHTML = `
            <!-- Agency Buttons (Row 1) -->
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

            <!-- Routes / Sub-Categories Buttons (Row 2) -->
            ${routeButtonsHtml}

            <!-- Day & Time Buttons (Row 3) -->
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

                // If agency changed, reset route & city filters to 'all' and re-render buttons
                if (filterKey === 'p') {
                    if (this.state.p !== filterVal) {
                        this.state.p = filterVal;
                        this.state.r = 'all';
                        this.state.c = 'all';
                        this.render();
                        this.onFilterChange(this.state);
                        return;
                    }
                }

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
