import { t } from '../i18n.js';

export class BusCard {
    constructor(routeData, onNoteClick, options = {}) {
        this.data = routeData;
        this.onNoteClick = onNoteClick;
        this.isToday = options.isToday ?? true;
        this.curMins = options.curMins ?? 0;
    }

    static formatCountdown(diffMins) {
        if (diffMins <= 0) return t('now');
        if (diffMins < 60) return t('inMin', { m: diffMins });
        const h = Math.floor(diffMins / 60);
        const m = diffMins % 60;
        return m > 0 ? t('inHours', { h, m }) : `${h}h`;
    }

    render() {
        const card = document.createElement('div');
        card.className = 'card';

        const dayBadges = t('dayBadges') || {};
        const dayBadgeText = dayBadges[this.data.type] || (this.data.type !== 'all' ? this.data.type : '');
        const dayBadge = dayBadgeText ? `<span class="day-badge">${dayBadgeText}</span>` : '';

        // Find next departure if today
        let nextDep = null;
        if (this.isToday && this.curMins > 0) {
            for (const timeObj of this.data.times) {
                const txt = (timeObj.t || '').replace(/[^\d:]/g, '');
                if (!txt || !txt.includes(':')) continue;

                const [h, m] = txt.split(':').map(Number);
                let busMins = h * 60 + m;

                let effectiveBus = busMins;
                let effectiveCur = this.curMins;
                if (effectiveBus < 180) effectiveBus += 1440;
                if (effectiveCur < 180) effectiveCur += 1440;

                const diff = effectiveBus - effectiveCur;
                if (diff >= 0) {
                    nextDep = { time: timeObj.t, diffMins: diff };
                    break;
                }
            }
        }

        const timesHtml = this.data.times.map(tObj => {
            if (tObj.t === 'LINK') {
                return `<a href="${tObj.url || this.data.url}" target="_blank" class="t-btn t-link">${tObj.f}</a>`;
            }

            const noteTxt = tObj.note_txt ? tObj.note_txt.replace(/"/g, '&quot;') : '';

            let timeClass = '';
            let countdownSpan = '';

            if (this.isToday && this.curMins > 0) {
                const txt = (tObj.t || '').replace(/[^\d:]/g, '');
                if (txt && txt.includes(':')) {
                    const [h, m] = txt.split(':').map(Number);
                    let busMins = h * 60 + m;
                    let effectiveBus = busMins;
                    let effectiveCur = this.curMins;
                    if (effectiveBus < 180) effectiveBus += 1440;
                    if (effectiveCur < 180) effectiveCur += 1440;

                    const diff = effectiveBus - effectiveCur;
                    if (diff < 0) {
                        timeClass = 'past';
                    } else if (nextDep && tObj.t === nextDep.time && !timeClass) {
                        timeClass = 'next';
                        countdownSpan = `<span class="live-diff">${BusCard.formatCountdown(diff)}</span>`;
                    }
                }
            }

            // Fallback to explicit diffMins if present (e.g. from nearest filter)
            if (tObj.diffMins !== undefined && !countdownSpan) {
                countdownSpan = `<span class="live-diff">${BusCard.formatCountdown(tObj.diffMins)}</span>`;
            }

            return `
                <div class="time-wrap">
                    <div class="t-btn ${timeClass} ${noteTxt ? 'clickable has-note' : ''}" 
                         data-time="${tObj.t}" 
                         data-star="${tObj.n || ''}" 
                         data-note="${noteTxt}">
                         ${tObj.t}<sup>${tObj.n || ''}</sup>
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
        let displayDesc = escapeHtml(this.data.desc);

        // Remove redundant day labels from description
        const dayStrings = ['(Будни)', '(Сб/Вс)', '(Пн)', '(Вт)', '(Ср)', '(Чт)', '(Пт)', '(Сб)', '(Вс)', '(Ежедневно)', '(Daily)', '(Weekday)', '(Weekend)'];
        dayStrings.forEach(ds => {
            if (displayDesc.includes(ds)) {
                displayDesc = displayDesc.replace(ds, '').trim();
            }
        });

        let displayTitle = safeTitle;
        if (displayTitle.includes('↔') && displayDesc.includes('➝')) {
            displayTitle = displayDesc;
            displayDesc = '';
        } else if (displayDesc === 'Route Schedule' || displayDesc === 'All stops') {
            displayDesc = '';
        }

        const favKey = `${this.data.prov}_${this.data.name}_${this.data.desc}`;
        const isFav = this.data.isFav ? 'active' : '';

        // Badges
        const priceHtml = this.data.price
            ? `<span class="price-badge">${escapeHtml(this.data.price)}</span>`
            : '';

        const durationHtml = this.data.duration
            ? `<span class="duration-badge">⏱ ${escapeHtml(this.data.duration)}</span>`
            : '';

        const nextChipHtml = (nextDep && this.isToday)
            ? `<span class="next-chip">⚡ ${t('nextDeparture')}: <b>${nextDep.time}</b> (${BusCard.formatCountdown(nextDep.diffMins)})</span>`
            : '';

        const errorHtml = this.data.hasError
            ? `<div class="c-error-banner">⚠️ ${escapeHtml(this.data.errorMsg)}</div>`
            : '';

        const descHtml = displayDesc ? `<div class="c-desc">${displayDesc}</div>` : '';

        card.innerHTML = `
            <div class="c-head">
                <div>
                    <div class="c-title-row">
                        <span class="c-title">${displayTitle}</span>
                        ${dayBadge}
                        ${priceHtml}
                        ${durationHtml}
                        ${nextChipHtml}
                    </div>
                    ${descHtml}
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

        // Bind note click
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
