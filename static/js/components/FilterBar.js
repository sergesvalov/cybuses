export class FilterBar {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        this.state = {
            p: 'all', // provider
            d: 'auto' // day type
        };
    }

    render() {
        this.container.innerHTML = `
            <div class="filter-group">
                <div class="f-label">Агентство</div>
                <div class="scroll-row" id="agency-filters">
                    <button class="d-btn active" data-filter="p" data-val="all">Все</button>
                    <button class="d-btn" data-filter="p" data-val="intercity">Intercity</button>
                    <button class="d-btn" data-filter="p" data-val="osypa">City (Osypa)</button>
                    <button class="d-btn" data-filter="p" data-val="shuttle">Airport</button>
                </div>
            </div>

            <div class="filter-group">
                <div class="f-label">День недели / Время</div>
                <div class="scroll-row" id="day-filters">
                    <button class="d-btn active" data-filter="d" data-val="auto">Авто</button>
                    <button class="d-btn" data-filter="d" data-val="weekday">Будни</button>
                    <button class="d-btn" data-filter="d" data-val="weekend">Выходные</button>
                    <button class="d-btn" data-filter="d" data-val="nearest">Ближайшие</button>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const buttons = this.container.querySelectorAll('.d-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.currentTarget;
                const filterKey = target.getAttribute('data-filter');
                const filterVal = target.getAttribute('data-val');

                // Update UI state
                target.parentElement.querySelectorAll('.d-btn').forEach(b => b.classList.remove('active'));
                target.classList.add('active');

                // Update local state and trigger callback
                this.state[filterKey] = filterVal;
                this.onFilterChange(this.state);
            });
        });
    }

    getState() {
        return this.state;
    }
}
