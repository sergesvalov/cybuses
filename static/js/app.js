import { Api } from './api.js';

class BusApp {
    constructor() {
        this.data = [];
        this.state = {
            p: 'all', // Provider filter
            d: 'auto' // Day type filter
        };

        this.appEl = document.getElementById('app');
        this.modalEl = document.getElementById('modal');
        this.refreshBtn = document.getElementById('r-btn');

        this.bindEvents();
    }

    bindEvents() {
        // Expose bound methods to window to allow HTML inline event handlers (onclick) to function.
        window.setF = this.setFilter.bind(this);
        window.showN = this.showNote.bind(this);
        window.closeM = this.closeModal.bind(this);
        window.refresh = this.refresh.bind(this);

        // Modal background click
        this.modalEl.addEventListener('click', (e) => {
            if (e.target === this.modalEl) {
                this.closeModal();
            }
        });

        // Initialize polling for time highlighting
        setInterval(() => this.highlightNext(), 60000);
    }

    getCurrentDayType() {
        const day = new Date().getDay();
        // 0 = Sunday, 6 = Saturday
        return (day === 0 || day === 6) ? 'weekend' : 'weekday';
    }

    async load() {
        this.appEl.innerHTML = '<div class="loader">Загрузка расписания...</div>';
        try {
            this.data = await Api.fetchData();
            this.render();
        } catch (e) {
            this.appEl.innerHTML = '<div class="loader">Ошибка загрузки</div>';
            console.error(e);
        }
    }

    render() {
        this.appEl.innerHTML = '';

        const activeDayType = this.state.d === 'auto' ? this.getCurrentDayType() : this.state.d;

        const fData = this.data.filter(route => {
            const matchProv = (this.state.p === 'all' || route.prov === this.state.p);
            const matchDay = (route.type === 'all' || route.type === activeDayType);
            return matchProv && matchDay;
        });

        if (!fData.length) {
            this.appEl.innerHTML = '<div class="loader">Рейсов не найдено</div>';
            return;
        }

        fData.forEach(r => {
            const card = document.createElement('div');
            card.className = 'card';

            const dayBadge = r.type !== 'all' ? `<span class="day-badge">${r.type === 'weekday' ? 'Будни' : 'Сб/Вс'}</span>` : '';

            const timesHtml = r.times.map(t => {
                if (t.t === 'LINK') {
                    return `<a href="${t.url || r.url}" target="_blank" class="t-btn" style="grid-column: 1/-1; text-decoration:none; background:var(--p); color:#fff;">${t.f}</a>`;
                }
                const noteTxt = t.note_txt ? t.note_txt.replace(/"/g, '&quot;') : '';
                const action = noteTxt ? `onclick="showN('${t.t}', '${t.n}', '${noteTxt}')"` : '';
                return `<div class="t-btn ${noteTxt ? 'has-note' : ''}" ${action}>${t.t}<sup>${t.n || ''}</sup></div>`;
            }).join('');

            card.innerHTML = `
                <div class="c-head">
                    <div>
                        <span class="c-title">${r.name}</span>${dayBadge}
                        <div class="c-desc">${r.desc}</div>
                    </div>
                    <a href="${r.url}" target="_blank" style="color:var(--p);text-decoration:none;font-size:1.2rem">↗</a>
                </div>
                <div class="times-grid">${timesHtml}</div>
            `;
            this.appEl.appendChild(card);
        });

        this.highlightNext();
    }

    setFilter(key, value, el) {
        this.state[key] = value;
        el.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        el.classList.add('active');
        this.render();
    }

    highlightNext() {
        const now = new Date();
        const curMins = now.getHours() * 60 + now.getMinutes();

        document.querySelectorAll('.card').forEach(card => {
            let foundNext = false;
            card.querySelectorAll('.t-btn').forEach(btn => {
                const txt = btn.innerText.replace(/[^\d:]/g, '');
                if (!txt || txt.length < 4) return;
                const [h, m] = txt.split(':').map(Number);
                let busMins = h * 60 + m;

                let effectiveBus = busMins;
                let effectiveCur = curMins;
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

    showNote(t, s, n) {
        document.getElementById('m-t').innerText = t + s;
        document.getElementById('m-n').innerText = n;
        this.modalEl.style.display = 'flex';
    }

    closeModal() {
        this.modalEl.style.display = 'none';
    }

    async refresh() {
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
