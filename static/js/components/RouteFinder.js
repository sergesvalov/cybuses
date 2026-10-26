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

    matchRoute(route) {
        const { from, to } = this.state;
        if (from === 'any' && to === 'any') return true;

        const desc = (route.desc || '').toLowerCase();
        const name = (route.name || '').toLowerCase();
        const combined = `${name} ${desc}`;

        const cityKeywords = {
            paphos: ['paphos', 'pafos', 'пафос'],
            limassol: ['limassol', 'lemesos', 'лимассол'],
            nicosia: ['nicosia', 'lefkosia', 'никосия'],
            larnaca: ['larnaca', 'ларнака'],
            paralimni: ['paralimni', 'ayia napa', 'паралимни', 'айя-напа'],
            paphos_airport: ['paphos airport', 'аэропорт пафос', '612', '613', 'airport', 'аэропорт'],
            larnaca_airport: ['larnaca airport', 'аэропорт ларнака', 'lca']
        };

        // Directional route: "CityA ➝ CityB"
        if (desc.includes('➝') || desc.includes('→')) {
            const parts = desc.split(/[➝→]/).map(s => s.trim().toLowerCase());
            const srcPart = parts[0];
            const dstPart = parts[parts.length - 1];

            if (from !== 'any') {
                const fromKw = cityKeywords[from] || [from];
                const matchFrom = fromKw.some(k => srcPart.includes(k) || (from === 'paphos_airport' && (srcPart.includes('airport') || route.prov === 'osypa')));
                if (!matchFrom) return false;
            }

            if (to !== 'any') {
                const toKw = cityKeywords[to] || [to];
                const matchTo = toKw.some(k => dstPart.includes(k) || (to === 'paphos_airport' && (dstPart.includes('airport') || route.prov === 'osypa')));
                if (!matchTo) return false;
            }

            return true;
        }

        // Generic airport / shuttle routes
        if (from === 'paphos_airport' || to === 'paphos_airport') {
            const isPaphosAirport = combined.includes('airport') && (combined.includes('paphos') || combined.includes('612') || combined.includes('613') || route.prov === 'osypa');
            if (!isPaphosAirport) return false;
        }

        if (from === 'larnaca_airport' || to === 'larnaca_airport') {
            const isLarnacaAirport = combined.includes('larnaca') && (combined.includes('airport') || combined.includes('kapnos') || combined.includes('express'));
            if (!isLarnacaAirport) return false;
        }

        if (from !== 'any' && from !== 'paphos_airport' && from !== 'larnaca_airport') {
            const fromKw = cityKeywords[from] || [from];
            if (!fromKw.some(k => combined.includes(k))) return false;
        }

        if (to !== 'any' && to !== 'paphos_airport' && to !== 'larnaca_airport') {
            const toKw = cityKeywords[to] || [to];
            if (!toKw.some(k => combined.includes(k))) return false;
        }

        return true;
    }
}
