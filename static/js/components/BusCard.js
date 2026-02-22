export class BusCard {
    constructor(routeData, onNoteClick) {
        this.data = routeData;
        this.onNoteClick = onNoteClick;
    }

    render() {
        const card = document.createElement('div');
        card.className = 'card';

        const dayMap = {
            'weekday': 'Будни',
            'weekend': 'Сб/Вс',
            'monday': 'Пн',
            'tuesday': 'Вт',
            'wednesday': 'Ср',
            'thursday': 'Чт',
            'friday': 'Пт',
            'saturday': 'Сб',
            'sunday': 'Вс',
            'all': ''
        };
        const dayBadge = this.data.type !== 'all'
            ? `<span class="day-badge">${dayMap[this.data.type] || this.data.type}</span>`
            : '';

        const timesHtml = this.data.times.map(t => {
            if (t.t === 'LINK') {
                return `<a href="${t.url || this.data.url}" target="_blank" class="t-btn t-link">${t.f}</a>`;
            }
            const noteTxt = t.note_txt ? t.note_txt.replace(/"/g, '&quot;') : '';
            const countdownSpan = t.diffMins ? `<span class="live-diff">через ${t.diffMins}'</span>` : '';
            return `
                <div class="time-wrap">
                    <div class="t-btn ${noteTxt ? 'clickable has-note' : ''}" 
                         data-time="${t.t}" 
                         data-star="${t.n || ''}" 
                         data-note="${noteTxt}">
                         ${t.t}<sup>${t.n || ''}</sup>
                    </div>
                    ${countdownSpan}
                </div>`;
        }).join('');

        const escapeHtml = (unsafe) => {
            if (!unsafe) return '';
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const safeTitle = escapeHtml(this.data.name);
        const safeDesc = escapeHtml(this.data.desc);

        // Check if favorited
        const favKey = `${this.data.prov}_${this.data.name}_${this.data.desc}`;
        const isFav = this.data.isFav ? 'active' : '';

        // Error Banner
        const errorHtml = this.data.hasError
            ? `<div class="c-error-banner">⚠️ ${escapeHtml(this.data.errorMsg)}</div>`
            : '';

        card.innerHTML = `
            <div class="c-head">
                <div>
                    <span class="c-title">${safeTitle} ${dayBadge}</span>
                    <div class="c-desc">${safeDesc}</div>
                </div>
                <div class="c-actions">
                    <button class="icon-btn fav-btn ${isFav}" data-key="${favKey}" aria-label="Favorite route">
                        <svg width="22" height="22" fill="${isFav ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                    </button>
                    <a href="${this.data.url}" target="_blank" class="link-icon" aria-label="Open source">
                        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 0 0 1-2-2V8a2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line>
                        </svg>
                    </a>
                </div>
            </div>
            ${errorHtml}
            <div class="c-times">${timesHtml}</div>
        `;

        // Bind note clicks
        card.querySelectorAll('.t-btn').forEach(btn => {
            if (!btn.classList.contains('t-link')) {
                btn.addEventListener('click', (e) => {
                    const tar = e.currentTarget;
                    if (tar.getAttribute('data-note')) {
                        this.onNoteClick(
                            tar.getAttribute('data-time'),
                            tar.getAttribute('data-star'),
                            tar.getAttribute('data-note')
                        );
                    }
                });
            }
        });

        return card;
    }
}
