HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>Paphos Bus Board</title>
    <style>
        :root { --p: #007bff; --bg: #f2f4f7; --card: #fff; }
        body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg); margin: 0; padding: 15px; color: #333; -webkit-tap-highlight-color: transparent; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .refresh-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; transition: 0.3s; }
        .spinning { animation: spin 1s linear infinite; opacity: 0.5; }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        .scroll-row { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 5px; margin-bottom: 12px; scrollbar-width: none; }
        .scroll-row::-webkit-scrollbar { display: none; }

        .d-btn { padding: 10px 14px; background: #fff; border: 1px solid #ddd; border-radius: 12px; font-weight: bold; flex-shrink: 0; cursor: pointer; }
        .d-btn.active { background: var(--p); color: #fff; border-color: var(--p); }
        .d-btn.today { border: 2px solid var(--p); color: var(--p); }
        .d-btn.today.active { color: #fff; }

        .p-btn { padding: 8px 14px; background: #fff; border: 1px solid #ddd; border-radius: 20px; font-weight: 600; white-space: nowrap; font-size: 0.9rem; cursor: pointer; }
        .p-btn.active { background: #333; color: #fff; border-color: #333; }
        .p-btn[data-p="intercity"].active { background: #198754; border-color: #198754; }
        .p-btn[data-p="osypa"].active { background: #00bfff; border-color: #00bfff; }

        .t-filter { display: flex; background: #e9ecef; border-radius: 10px; padding: 4px; margin-bottom: 15px; }
        .t-tab { flex: 1; border: none; background: transparent; padding: 8px; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 0.9rem; }
        .t-tab.active { background: #fff; color: var(--p); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

        .hours-cont { display: none; gap: 6px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 10px; scrollbar-width: none; animation: fadeIn 0.3s ease; }
        .hours-cont.show { display: flex; }
        .h-btn { padding: 10px 0; width: 55px; text-align: center; background: #fff; border: 1px solid #ccc; border-radius: 10px; font-weight: bold; flex-shrink: 0; cursor: pointer; }
        .h-btn.active { background: var(--p); color: white; border-color: var(--p); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

        .card { background: var(--card); border-radius: 16px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #ccc; }
        .card.intercity { border-left-color: #198754; }
        .card.osypa { border-left-color: #00bfff; }
        .c-head { margin-bottom: 10px; }
        .c-title { font-weight: 800; font-size: 1.05rem; }
        .c-desc { font-size: 0.8rem; color: #888; text-transform: uppercase; margin-top: 2px; font-weight: 700; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(55px, 1fr)); gap: 6px; }
        .time { background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; padding: 8px 0; text-align: center; font-weight: 700; font-size: 0.9rem; }
        .time.note { border-bottom: 3px solid #ffc107; cursor: help; }
        .time.hl { background: #fff3cd; border-color: #ffeeba; }
        .time.link { grid-column: 1 / -1; background: var(--p); color: #fff; text-decoration: none; padding: 12px; border-radius: 8px; }

        .modal { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 100; backdrop-filter: blur(2px); }
        .box { background: #fff; padding: 25px; border-radius: 20px; width: 85%; max-width: 320px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .close-btn { background: #333; color: white; border: none; padding: 10px 20px; border-radius: 20px; margin-top: 15px; font-weight: bold; cursor: pointer; width: 100%; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Bus Paphos</h2>
        <button class="refresh-btn" onclick="refresh()" id="r-btn">↻</button>
    </div>
    <div class="scroll-row" id="d-cont"></div>
    <div class="scroll-row">
        <button class="p-btn active" onclick="setF('p','all',this)">Все</button>
        <button class="p-btn" data-p="intercity" onclick="setF('p','intercity',this)">Intercity</button>
        <button class="p-btn" data-p="osypa" onclick="setF('p','osypa',this)">OSYPA</button>
        <button class="p-btn" data-p="kapnos" onclick="setF('p','kapnos',this)">Kapnos</button>
        <button class="p-btn" data-p="lim_express" onclick="setF('p','lim_express',this)">Express</button>
    </div>
    <div class="t-filter" id="t-cont">
        <button class="t-tab active" id="btn-all" onclick="setF('t','all',this)">Весь день</button>
        <button class="t-tab" id="btn-hour" onclick="setF('t','hour',this)">По часам</button>
        <button class="t-tab" id="btn-next" onclick="setF('t','next',this)">Ближайшие</button>
    </div>
    <div class="hours-cont" id="h-slider"></div>
    <div id="app"></div>
    <div class="modal" id="modal" onclick="if(event.target==this)closeM()">
        <div class="box">
            <h3 id="m-t" style="margin-top:0"></h3>
            <p id="m-n" style="color:#555; line-height:1.5"></p>
            <button class="close-btn" onclick="closeM()">Понятно</button>
        </div>
    </div>
    <script>
        let DATA = [];
        let STATE = { p: 'all', t: 'all', d: new Date().getDay(), h: new Date().getHours() };
        const TODAY = new Date().getDay();
        const DAYS = ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'];

        const dDiv = document.getElementById('d-cont');
        for(let i=0; i<7; i++) {
            const idx = (i + 1) % 7; 
            const b = document.createElement('button');
            b.className = `d-btn ${idx===TODAY?'today active':''}`;
            b.innerText = DAYS[idx];
            b.onclick = () => {
                document.querySelectorAll('.d-btn').forEach(x=>x.classList.remove('active'));
                b.classList.add('active'); 
                STATE.d = idx;
                const btnNext = document.getElementById('btn-next');
                if(idx !== TODAY) {
                    if(STATE.t === 'next') setF('t','all', document.getElementById('btn-all'));
                    btnNext.style.opacity = '0.4'; btnNext.style.pointerEvents = 'none';
                } else {
                    btnNext.style.opacity = '1'; btnNext.style.pointerEvents = 'auto';
                }
                render();
            };
            dDiv.appendChild(b);
        }

        const hDiv = document.getElementById('h-slider');
        for(let i=4; i<=23; i++) {
            const b = document.createElement('button');
            b.className = 'h-btn';
            b.innerText = `${i}:00`;
            b.onclick = () => {
                STATE.h = i;
                document.querySelectorAll('.h-btn').forEach(x=>x.classList.remove('active'));
                b.classList.add('active');
                render();
            };
            if(i === STATE.h) b.classList.add('active');
            hDiv.appendChild(b);
        }

        async function load() { 
            try { const r = await fetch('/api/data'); DATA = await r.json(); render(); } catch(e){}
        }

        function render() {
            const app = document.getElementById('app'); app.innerHTML = '';
            const now = new Date();
            const cm = now.getHours()*60 + now.getMinutes();
            const isWE = (STATE.d===0 || STATE.d===6);
            let hasResults = false;

            DATA.forEach((block) => {
                if(STATE.p !== 'all' && block.prov !== STATE.p) return;
                if(block.type==='weekday' && isWE) return; 
                if(block.type==='weekend' && !isWE) return;

                let html = '';
                let count = 0, nFound = 0;

                block.times.forEach(t => {
                    if(t.t === 'LINK') { 
                        if(STATE.t === 'all') {
                            html += `<a href="${block.url}" target="_blank" class="time link">${t.f}</a>`;
                            count++;
                        }
                        return; 
                    }

                    const [h, m] = t.t.split(':').map(Number);
                    const val = h*60 + m;
                    let show = false, highlight = false;

                    if (STATE.t === 'all') show = true;
                    else if (STATE.t === 'next') {
                        if (STATE.d === TODAY && val >= cm && nFound < 2) {
                            show = true; highlight = true; nFound++;
                        }
                    } 
                    else if (STATE.t === 'hour') {
                        if (h === STATE.h) { show = true; highlight = true; }
                    }

                    if(show) {
                        const noteCl = t.n ? 'note' : '';
                        const hlCl = highlight ? 'hl' : '';
                        const click = t.n ? `onclick="event.stopPropagation();showN('${t.t}','${t.n}','${block.notes[t.n]}')"` : '';
                        html += `<div class="time ${noteCl} ${hlCl}" ${click}>${t.f}</div>`;
                        count++;
                    }
                });

                if(count > 0) {
                    hasResults = true;
                    const d = document.createElement('div'); 
                    d.className = `card ${block.prov}`;
                    d.innerHTML = `<div class="c-head"><div class="c-title">${block.name}</div><div class="c-desc">${block.desc}</div></div><div class="grid">${html}</div>`;
                    app.appendChild(d);
                }
            });

            if(!hasResults) {
                const msg = STATE.t === 'hour' ? `В ${STATE.h}:00 рейсов нет` : 'Рейсов не найдено';
                app.innerHTML = `<div style="text-align:center;color:#999;margin-top:60px">${msg}</div>`;
            }
        }

        function setF(k, v, el) { 
            STATE[k] = v;
            el.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            const slider = document.getElementById('h-slider');
            if (k === 't' && v === 'hour') {
                slider.classList.add('show');
                setTimeout(() => {
                    const activeH = slider.querySelector('.active');
                    if(activeH) activeH.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                }, 100);
            } else if (k === 't') slider.classList.remove('show');
            render(); 
        }

        function showN(t,s,n) { 
            document.getElementById('m-t').innerText = t+s; 
            document.getElementById('m-n').innerText = n || '...'; 
            document.getElementById('modal').style.display='flex'; 
        }
        function closeM() { document.getElementById('modal').style.display='none'; }
        async function refresh() {
            const btn = document.getElementById('r-btn'); btn.classList.add('spinning');
            await fetch('/api/refresh', {method:'POST'});
            const iv = setInterval(async () => {
                const s = await (await fetch('/api/status')).json();
                if(!s.updating) { clearInterval(iv); btn.classList.remove('spinning'); load(); }
            }, 2000);
        }
        load();
    </script>
</body>
</html>
"""