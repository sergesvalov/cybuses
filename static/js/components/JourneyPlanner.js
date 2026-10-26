import { t, getLang } from '../i18n.js?v=10';
import { RouteFinder } from './RouteFinder.js?v=10';

export const HUB_NAMES = {
    ru: {
        paphos: "Пафос",
        limassol: "Лимассол",
        nicosia: "Никосия",
        larnaca: "Ларнака",
        paralimni: "Паралимни / Айя-Напа",
        polis: "Полис / Лачи",
        paphos_airport: "Аэропорт Пафос (PFO)",
        larnaca_airport: "Аэропорт Ларнака (LCA)"
    },
    en: {
        paphos: "Paphos",
        limassol: "Limassol",
        nicosia: "Nicosia",
        larnaca: "Larnaca",
        paralimni: "Paralimni / Ayia Napa",
        polis: "Polis / Latchi",
        paphos_airport: "Paphos Airport (PFO)",
        larnaca_airport: "Larnaca Airport (LCA)"
    }
};

export class JourneyPlanner {
    static getHubName(hubKey) {
        const lang = getLang();
        const dict = HUB_NAMES[lang] || HUB_NAMES.ru;
        return dict[hubKey] || hubKey;
    }

    static parseDurationMinutes(durStr) {
        if (!durStr) return 60;
        let mins = 0;
        const hMatch = durStr.match(/(\d+)\s*h/i);
        const mMatch = durStr.match(/(\d+)\s*m/i);
        if (hMatch) mins += parseInt(hMatch[1], 10) * 60;
        if (mMatch) mins += parseInt(mMatch[1], 10);
        return mins > 0 ? mins : 60;
    }

    static toMins(timeStr) {
        if (!timeStr || !timeStr.includes(':')) return 0;
        const [h, m] = timeStr.split(':').map(Number);
        return h * 60 + m;
    }

    static toTimeStr(mins) {
        const h = Math.floor(mins / 60) % 24;
        const m = mins % 60;
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }

    static formatDuration(totalMins) {
        const h = Math.floor(totalMins / 60);
        const m = totalMins % 60;
        const lang = getLang();
        if (h === 0) return `${m} ${lang === 'ru' ? 'мин' : 'min'}`;
        if (m === 0) return `${h} ${lang === 'ru' ? 'ч' : 'h'}`;
        return lang === 'ru' ? `${h} ч ${m} мин` : `${h}h ${m}m`;
    }

    /**
     * Builds directed edges graph from the routes data.
     */
    static buildEdges(routesData, dayType = 'weekday') {
        const edges = new Map();
        const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        const weekends = ['saturday', 'sunday'];

        routesData.forEach(route => {
            // Day matching
            let matchDay = false;
            if (route.type === 'all') {
                matchDay = true;
            } else if (dayType === 'weekday') {
                matchDay = (route.type === 'weekday' || weekdays.includes(route.type));
            } else if (dayType === 'weekend') {
                matchDay = (route.type === 'weekend' || weekends.includes(route.type));
            }
            if (!matchDay) return;

            const desc = route.desc || '';
            const name = route.name || '';
            const prov = route.prov || '';
            const durMins = JourneyPlanner.parseDurationMinutes(route.duration);

            let fLoc = null;
            let tLoc = null;

            if (desc.includes('➝') || desc.includes('→')) {
                const parts = desc.split(/[➝→]/).map(s => s.trim());
                fLoc = RouteFinder.resolveLocation(parts[0], prov);
                tLoc = RouteFinder.resolveLocation(parts[parts.length - 1], prov);
            } else if (name.includes('↔')) {
                const parts = name.split('↔').map(s => s.trim());
                fLoc = RouteFinder.resolveLocation(parts[0], prov);
                tLoc = RouteFinder.resolveLocation(parts[1], prov);
            }

            if (fLoc && tLoc && fLoc !== tLoc) {
                const key = `${fLoc}__${tLoc}`;
                if (!edges.has(key)) edges.set(key, []);

                const validTimes = (route.times || [])
                    .map(tObj => tObj.t)
                    .filter(tStr => tStr && tStr.includes(':'));

                edges.get(key).push({
                    name: route.name,
                    desc: route.desc,
                    prov: route.prov,
                    duration_mins: durMins,
                    duration_str: route.duration || `~ ${durMins}m`,
                    price: route.price || '€5',
                    times: validTimes
                });
            }
        });

        return edges;
    }

    /**
     * Plans multi-leg itineraries between Origin and Destination based on real timetable synchronization.
     */
    static planJourney(routesData, origin, destination, options = {}) {
        if (!origin || !destination || origin === 'any' || destination === 'any' || origin === destination) {
            return [];
        }

        const curMins = options.curMins ?? 0;
        const dayType = options.dayType ?? 'weekday';
        const edges = JourneyPlanner.buildEdges(routesData, dayType);
        const hubs = ['paphos', 'limassol', 'nicosia', 'larnaca', 'paralimni', 'polis', 'paphos_airport', 'larnaca_airport'];
        const itineraries = [];

        // 1. DIRECT JOURNEYS
        const directKey = `${origin}__${destination}`;
        if (edges.has(directKey)) {
            edges.get(directKey).forEach(r => {
                r.times.forEach(tStr => {
                    const dep = JourneyPlanner.toMins(tStr);
                    // Include upcoming trips or trips within last 20 mins
                    if (dep < curMins - 20) return;
                    const arr = dep + r.duration_mins;
                    itineraries.push({
                        type: 'direct',
                        transfers: 0,
                        transferPoints: [],
                        depMins: dep,
                        arrMins: arr,
                        totalMins: r.duration_mins,
                        legs: [{
                            from: origin,
                            to: destination,
                            name: r.name,
                            desc: r.desc,
                            prov: r.prov,
                            depTime: tStr,
                            arrTime: JourneyPlanner.toTimeStr(arr),
                            durationStr: r.duration_str,
                            price: r.price
                        }]
                    });
                });
            });
        }

        // 2. ONE-TRANSFER JOURNEYS (Origin -> Mid -> Destination)
        hubs.forEach(mid => {
            if (mid === origin || mid === destination) return;
            const k1 = `${origin}__${mid}`;
            const k2 = `${mid}__${destination}`;

            if (edges.has(k1) && edges.has(k2)) {
                edges.get(k1).forEach(r1 => {
                    r1.times.forEach(t1 => {
                        const dep1 = JourneyPlanner.toMins(t1);
                        if (dep1 < curMins - 20) return;
                        const arr1 = dep1 + r1.duration_mins;

                        edges.get(k2).forEach(r2 => {
                            r2.times.forEach(t2 => {
                                const dep2 = JourneyPlanner.toMins(t2);
                                const waitMins = dep2 - arr1;
                                // Transfer layover cushion: minimum 10 min, max 150 min
                                if (waitMins >= 10 && waitMins <= 150) {
                                    const arr2 = dep2 + r2.duration_mins;
                                    itineraries.push({
                                        type: '1_transfer',
                                        transfers: 1,
                                        transferPoints: [mid],
                                        depMins: dep1,
                                        arrMins: arr2,
                                        totalMins: arr2 - dep1,
                                        legs: [
                                            {
                                                from: origin,
                                                to: mid,
                                                name: r1.name,
                                                desc: r1.desc,
                                                prov: r1.prov,
                                                depTime: t1,
                                                arrTime: JourneyPlanner.toTimeStr(arr1),
                                                durationStr: r1.duration_str,
                                                price: r1.price
                                            },
                                            {
                                                from: mid,
                                                to: destination,
                                                name: r2.name,
                                                desc: r2.desc,
                                                prov: r2.prov,
                                                depTime: t2,
                                                arrTime: JourneyPlanner.toTimeStr(arr2),
                                                durationStr: r2.duration_str,
                                                price: r2.price,
                                                waitMins: waitMins
                                            }
                                        ]
                                    });
                                }
                            });
                        });
                    });
                });
            }
        });

        // 3. TWO-TRANSFER JOURNEYS (Origin -> Mid1 -> Mid2 -> Destination)
        // Useful for Paphos -> Paralimni via Limassol + Larnaca, or Polis -> Paralimni
        hubs.forEach(m1 => {
            if (m1 === origin || m1 === destination) return;
            hubs.forEach(m2 => {
                if (m2 === origin || m2 === destination || m2 === m1) return;
                const k1 = `${origin}__${m1}`;
                const k2 = `${m1}__${m2}`;
                const k3 = `${m2}__${destination}`;

                if (edges.has(k1) && edges.has(k2) && edges.has(k3)) {
                    edges.get(k1).forEach(r1 => {
                        r1.times.forEach(t1 => {
                            const dep1 = JourneyPlanner.toMins(t1);
                            if (dep1 < curMins - 20) return;
                            const arr1 = dep1 + r1.duration_mins;

                            edges.get(k2).forEach(r2 => {
                                r2.times.forEach(t2 => {
                                    const dep2 = JourneyPlanner.toMins(t2);
                                    const wait1 = dep2 - arr1;
                                    if (wait1 < 10 || wait1 > 120) return;
                                    const arr2 = dep2 + r2.duration_mins;

                                    edges.get(k3).forEach(r3 => {
                                        r3.times.forEach(t3 => {
                                            const dep3 = JourneyPlanner.toMins(t3);
                                            const wait2 = dep3 - arr2;
                                            if (wait2 >= 10 && wait2 <= 120) {
                                                const arr3 = dep3 + r3.duration_mins;
                                                itineraries.push({
                                                    type: '2_transfers',
                                                    transfers: 2,
                                                    transferPoints: [m1, m2],
                                                    depMins: dep1,
                                                    arrMins: arr3,
                                                    totalMins: arr3 - dep1,
                                                    legs: [
                                                        {
                                                            from: origin,
                                                            to: m1,
                                                            name: r1.name,
                                                            desc: r1.desc,
                                                            prov: r1.prov,
                                                            depTime: t1,
                                                            arrTime: JourneyPlanner.toTimeStr(arr1),
                                                            durationStr: r1.duration_str,
                                                            price: r1.price
                                                        },
                                                        {
                                                            from: m1,
                                                            to: m2,
                                                            name: r2.name,
                                                            desc: r2.desc,
                                                            prov: r2.prov,
                                                            depTime: t2,
                                                            arrTime: JourneyPlanner.toTimeStr(arr2),
                                                            durationStr: r2.duration_str,
                                                            price: r2.price,
                                                            waitMins: wait1
                                                        },
                                                        {
                                                            from: m2,
                                                            to: destination,
                                                            name: r3.name,
                                                            desc: r3.desc,
                                                            prov: r3.prov,
                                                            depTime: t3,
                                                            arrTime: JourneyPlanner.toTimeStr(arr3),
                                                            durationStr: r3.duration_str,
                                                            price: r3.price,
                                                            waitMins: wait2
                                                        }
                                                    ]
                                                });
                                            }
                                        });
                                    });
                                });
                            });
                        });
                    });
                }
            });
        });

        // Deduplicate itineraries with identical departure and arrival signatures
        const seen = new Set();
        const unique = [];

        itineraries.forEach(it => {
            const sig = `${it.transfers}_${it.transferPoints.join('-')}_${it.legs[0].depTime}_${it.legs[it.legs.length - 1].arrTime}`;
            if (!seen.has(sig)) {
                seen.add(sig);
                unique.push(it);
            }
        });

        // Sort: Fewer transfers first, then earliest departure, then shortest total duration
        unique.sort((a, b) => {
            if (a.transfers !== b.transfers) return a.transfers - b.transfers;
            if (a.depMins !== b.depMins) return a.depMins - b.depMins;
            return a.totalMins - b.totalMins;
        });

        return unique.slice(0, 8); // Return top 8 best recommendations
    }

    /**
     * Renders a rich, interactive journey itinerary card.
     */
    static renderItineraryCard(itinerary) {
        const card = document.createElement('div');
        card.className = 'itinerary-card';

        const firstLeg = itinerary.legs[0];
        const lastLeg = itinerary.legs[itinerary.legs.length - 1];
        const originName = JourneyPlanner.getHubName(firstLeg.from);
        const destName = JourneyPlanner.getHubName(lastLeg.to);

        let badgeClass = 'direct-badge';
        let badgeText = `🟢 ${t('directTrip')}`;

        if (itinerary.transfers === 1) {
            badgeClass = 'transfer-badge';
            const midName = JourneyPlanner.getHubName(itinerary.transferPoints[0]);
            badgeText = `⚡ ${t('oneTransfer')} (${midName})`;
        } else if (itinerary.transfers >= 2) {
            badgeClass = 'multi-transfer-badge';
            const points = itinerary.transferPoints.map(p => JourneyPlanner.getHubName(p)).join(', ');
            badgeText = `⚡ ${t('twoTransfers')} (${points})`;
        }

        const durationFormatted = JourneyPlanner.formatDuration(itinerary.totalMins);

        let timelineHtml = '';
        itinerary.legs.forEach((leg, idx) => {
            const stepNum = idx + 1;
            const legFrom = JourneyPlanner.getHubName(leg.from);
            const legTo = JourneyPlanner.getHubName(leg.to);

            // Layover alert between legs
            if (idx > 0 && leg.waitMins) {
                timelineHtml += `
                    <div class="it-layover">
                        <div class="layover-icon">⏳</div>
                        <div class="layover-content">
                            <strong>${t('transferAt', { city: legFrom })}</strong>
                            <span>${t('transferWait', { m: leg.waitMins })}</span>
                        </div>
                    </div>
                `;
            }

            timelineHtml += `
                <div class="it-step">
                    <div class="it-step-badge">${stepNum}</div>
                    <div class="it-step-body">
                        <div class="it-step-header">
                            <span class="it-bus-name">🚌 ${leg.name}</span>
                            <span class="it-bus-prov ${leg.prov}">${leg.prov.toUpperCase()}</span>
                        </div>
                        <div class="it-step-times">
                            <div class="it-time-point">
                                <span class="it-time">${leg.depTime}</span>
                                <span class="it-place">${legFrom}</span>
                            </div>
                            <div class="it-arrow">➝ <span class="it-dur">${leg.durationStr}</span> ➝</div>
                            <div class="it-time-point">
                                <span class="it-time">${leg.arrTime}</span>
                                <span class="it-place">${legTo}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        card.innerHTML = `
            <div class="it-header">
                <div class="it-route-summary">
                    <span class="it-cities">${originName} ➔ ${destName}</span>
                    <span class="it-tag ${badgeClass}">${badgeText}</span>
                </div>
                <div class="it-metrics">
                    <div class="it-time-span">
                        <span class="it-start-time">${firstLeg.depTime}</span>
                        <span class="it-sep">➔</span>
                        <span class="it-end-time">${lastLeg.arrTime}</span>
                    </div>
                    <div class="it-total-dur">⏱ ${durationFormatted}</div>
                </div>
            </div>

            <div class="it-timeline">
                ${timelineHtml}
            </div>
        `;

        return card;
    }
}
