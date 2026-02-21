export class BusCard {
    constructor(routeData, onNoteClick) {
        this.data = routeData;
        this.onNoteClick = onNoteClick;
    }

    render() {
        const card = document.createElement('div');
        card.className = 'card';

        const dayBadge = this.data.type !== 'all'
            ? `<span class="day-badge">${this.data.type === 'weekday' ? 'Будни' : 'Сб/Вс'}</span>`
            : '';

        const timesHtml = this.data.times.map(t => {
            if (t.t === 'LINK') {
                return `<a href="${t.url || this.data.url}" target="_blank" class="t-btn t-link">${t.f}</a>`;
            }
            const noteTxt = t.note_txt ? t.note_txt.replace(/"/g, '&quot;') : '';
            return `
                <div class="t-btn ${noteTxt ? 'clickable has-note' : ''}" 
                     data-time="${t.t}" 
                     data-star="${t.n || ''}" 
                     data-note="${noteTxt}">
                     ${t.t}<sup>${t.n || ''}</sup>
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

        card.innerHTML = `
            <div class="c-head">
                <div>
                    <span class="c-title">${safeTitle} ${dayBadge}</span>
                    <div class="c-desc">${safeDesc}</div>
                </div>
                <a href="${this.data.url}" target="_blank" class="link-icon" aria-label="Open source">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                </a>
            </div>
            <div class="times-grid">${timesHtml}</div>
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
