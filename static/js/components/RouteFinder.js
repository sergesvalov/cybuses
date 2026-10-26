import { t } from '../i18n.js';

export class RouteFinder {
    constructor(containerId, onRouteChange) {
        this.container = document.getElementById(containerId);
        this.onRouteChange = onRouteChange;
        this.state = {
            from: 'any',
            to: 'any'
        };
    }

    render() {
        if (!this.container) return;

        const isSelected = (val, target) => val === target ? 'selected' : '';

        this.container.innerHTML = `
            <div class="route-finder-card">
                <div class="rf-title-row">
                    <span class="rf-title">🎯 ${t('directRoutes')}</span>
                    ${(this.state.from !== 'any' || this.state.to !== 'any') ? `<button class="rf-reset-btn" id="rf-reset" title="${t('reset')}">✕ ${t('reset')}</button>` : ''}
                </div>
                <div class="rf-controls">
                    <div class="rf-field">
                        <label class="rf-label" for="rf-from">${t('fromCity')}</label>
                        <select id="rf-from" class="rf-select">
                            <option value="any" ${isSelected('any', this.state.from)}>${t('anyCity')}</option>
                            <option value="paphos" ${isSelected('paphos', this.state.from)}>${t('paphos')}</option>
                            <option value="limassol" ${isSelected('limassol', this.state.from)}>${t('limassol')}</option>
                            <option value="nicosia" ${isSelected('nicosia', this.state.from)}>${t('nicosia')}</option>
                            <option value="larnaca" ${isSelected('larnaca', this.state.from)}>${t('larnaca')}</option>
                            <option value="paralimni" ${isSelected('paralimni', this.state.from)}>${t('paralimni')}</option>
                            <option value="paphos_airport" ${isSelected('paphos_airport', this.state.from)}>${t('paphosAirport')}</option>
                            <option value="larnaca_airport" ${isSelected('larnaca_airport', this.state.from)}>${t('larnacaAirport')}</option>
                        </select>
                    </div>

                    <button id="rf-swap" class="rf-swap-btn" aria-label="${t('swap')}" title="${t('swap')}">
                        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                            <path d="M7 16V4m0 0L3 8m4-4l4 4m6 4v12m0 0l4-4m-4 4l-4-4"/>
                        </svg>
                    </button>

                    <div class="rf-field">
                        <label class="rf-label" for="rf-to">${t('toCity')}</label>
                        <select id="rf-to" class="rf-select">
                            <option value="any" ${isSelected('any', this.state.to)}>${t('anyCity')}</option>
                            <option value="paphos" ${isSelected('paphos', this.state.to)}>${t('paphos')}</option>
                            <option value="limassol" ${isSelected('limassol', this.state.to)}>${t('limassol')}</option>
                            <option value="nicosia" ${isSelected('nicosia', this.state.to)}>${t('nicosia')}</option>
                            <option value="larnaca" ${isSelected('larnaca', this.state.to)}>${t('larnaca')}</option>
                            <option value="paralimni" ${isSelected('paralimni', this.state.to)}>${t('paralimni')}</option>
                            <option value="paphos_airport" ${isSelected('paphos_airport', this.state.to)}>${t('paphosAirport')}</option>
                            <option value="larnaca_airport" ${isSelected('larnaca_airport', this.state.to)}>${t('larnacaAirport')}</option>
                        </select>
                    </div>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const fromSelect = this.container.querySelector('#rf-from');
        const toSelect = this.container.querySelector('#rf-to');
        const swapBtn = this.container.querySelector('#rf-swap');
        const resetBtn = this.container.querySelector('#rf-reset');

        if (fromSelect) {
            fromSelect.addEventListener('change', (e) => {
                this.state.from = e.target.value;
                this.render();
                this.onRouteChange(this.state);
            });
        }

        if (toSelect) {
            toSelect.addEventListener('change', (e) => {
                this.state.to = e.target.value;
                this.render();
                this.onRouteChange(this.state);
            });
        }

        if (swapBtn) {
            swapBtn.addEventListener('click', () => {
                const temp = this.state.from;
                this.state.from = this.state.to;
                this.state.to = temp;
                this.render();
                this.onRouteChange(this.state);
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.state.from = 'any';
                this.state.to = 'any';
                this.render();
                this.onRouteChange(this.state);
            });
        }
    }

    getState() {
        return this.state;
    }

    static resolveLocation(text, prov = '') {
        if (!text) return null;
        const s = text.toLowerCase();

        // 1. Paphos Airport (PFO) - check specific airport terms first
        if (
            s.includes('paphos airport') ||
            s.includes('pafos airport') ||
            s.includes('аэропорт пафос') ||
            s.includes('аэропорта пафос') ||
            s.includes('pfo') ||
            ((prov === 'osypa' || s.includes('612') || s.includes('613')) && (s.includes('airport') || s.includes('аэропорт')))
        ) {
            return 'paphos_airport';
        }

        // 2. Larnaca Airport (LCA)
        if (
            s.includes('larnaca airport') ||
            s.includes('аэропорт ларнака') ||
            s.includes('аэропорта ларнака') ||
            s.includes('lca')
        ) {
            return 'larnaca_airport';
        }

        // 3. Paphos City (including OSYPA city stations: Harbour, Karavella, Tombs of the Kings, Market, Coral Bay, etc.)
        if (
            s.includes('paphos') ||
            s.includes('pafos') ||
            s.includes('пафос') ||
            s.includes('tombs of the kings') ||
            s.includes('karavela') ||
            s.includes('karavella') ||
            s.includes('harbour') ||
            s.includes('coral bay') ||
            s.includes('market') ||
            s.includes('waterpark') ||
            s.includes('petra') ||
            prov === 'osypa'
        ) {
            return 'paphos';
        }

        // 4. Limassol City
        if (
            s.includes('limassol') ||
            s.includes('lemesos') ||
            s.includes('лимассол') ||
            s.includes('havouza')
        ) {
            return 'limassol';
        }

        // 5. Nicosia City
        if (
            s.includes('nicosia') ||
            s.includes('lefkosia') ||
            s.includes('никосия')
        ) {
            return 'nicosia';
        }

        // 6. Larnaca City
        if (
            s.includes('larnaca') ||
            s.includes('ларнака')
        ) {
            return 'larnaca';
        }

        // 7. Paralimni / Ayia Napa
        if (
            s.includes('paralimni') ||
            s.includes('ayia napa') ||
            s.includes('паралимни') ||
            s.includes('айя-напа')
        ) {
            return 'paralimni';
        }

        return null;
    }

    matchRoute(route) {
        const { from, to } = this.state;
        if (from === 'any' && to === 'any') return true;

        const desc = route.desc || '';
        const name = route.name || '';
        const prov = route.prov || '';

        let routeFrom = null;
        let routeTo = null;

        // Check if description has directional arrow "Origin ➝ Destination"
        if (desc.includes('➝') || desc.includes('→')) {
            const parts = desc.split(/[➝→]/).map(s => s.trim());
            routeFrom = RouteFinder.resolveLocation(parts[0], prov);
            routeTo = RouteFinder.resolveLocation(parts[parts.length - 1], prov);
        } else if (name.includes('↔')) {
            const parts = name.split('↔').map(s => s.trim());
            const loc1 = RouteFinder.resolveLocation(parts[0], prov);
            const loc2 = RouteFinder.resolveLocation(parts[1], prov);
            if (from !== 'any' && to !== 'any') {
                return (from === loc1 && to === loc2) || (from === loc2 && to === loc1);
            }
            if (from !== 'any') return from === loc1 || from === loc2;
            if (to !== 'any') return to === loc1 || to === loc2;
            return true;
        } else if (name.toLowerCase().includes('kapnos')) {
            routeTo = 'larnaca_airport';
        }

        // Strict matching: route origin must match "from"
        if (from !== 'any') {
            if (routeFrom !== from) return false;
        }

        // Strict matching: route destination must match "to"
        if (to !== 'any') {
            if (routeTo !== to) return false;
        }

        return true;
    }
}
