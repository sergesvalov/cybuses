class AdminApp {
    constructor() {
        this.data = [];
        this.currentRouteId = null;
        this.currentDirId = null;

        // DOM elements
        this.routeList = document.getElementById('route-list');
        this.dirList = document.getElementById('dir-list');
        this.depList = document.getElementById('dep-list');
        
        this.dirSection = document.getElementById('directions-section');
        this.depSection = document.getElementById('departures-section');

        this.modal = document.getElementById('admin-modal');
        this.modalTitle = document.getElementById('am-title');
        this.modalForm = document.getElementById('am-form');
        this.modalFields = document.getElementById('am-fields');
        
        this.bindEvents();
    }

    async load() {
        try {
            const res = await fetch('/api/admin/data');
            if (res.status === 401) {
                alert("Unauthorized");
                return;
            }
            this.data = await res.json();
            this.renderRoutes();
            if (this.currentRouteId) this.renderDirections(this.currentRouteId);
            if (this.currentDirId) this.renderDepartures(this.currentDirId);
        } catch (e) {
            console.error(e);
        }
    }

    bindEvents() {
        document.getElementById('btn-add-route').addEventListener('click', () => this.showModal('route'));
        document.getElementById('btn-import-route').addEventListener('click', () => this.showModal('bulk'));
        document.getElementById('btn-add-dir').addEventListener('click', () => this.showModal('direction'));
        document.getElementById('btn-add-dep').addEventListener('click', () => this.showModal('departure'));
        
        document.getElementById('am-close').addEventListener('click', () => this.closeModal());
        document.getElementById('am-overlay').addEventListener('click', () => this.closeModal());
        
        this.modalForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    renderRoutes() {
        this.routeList.innerHTML = '';
        this.data.forEach(r => {
            const el = document.createElement('div');
            el.className = `admin-item ${this.currentRouteId === r.id ? 'active' : ''}`;
            el.innerHTML = `
                <div>
                    <strong>${r.name}</strong> <span class="badge">${r.provider}</span>
                </div>
                <div class="actions">
                    <button class="btn-text btn-edit" data-id="${r.id}">Edit</button>
                    <button class="btn-text btn-del" data-id="${r.id}">Del</button>
                </div>
            `;
            
            el.addEventListener('click', (e) => {
                if (e.target.tagName !== 'BUTTON') {
                    this.currentRouteId = r.id;
                    this.currentDirId = null;
                    this.renderRoutes();
                    this.renderDirections(r.id);
                }
            });

            const btnEdit = el.querySelector('.btn-edit');
            btnEdit.addEventListener('click', () => this.showModal('route', r));

            const btnDel = el.querySelector('.btn-del');
            btnDel.addEventListener('click', () => this.deleteEntity('routes', r.id));

            this.routeList.appendChild(el);
        });
    }

    renderDirections(routeId) {
        this.dirSection.classList.remove('hidden');
        this.depSection.classList.add('hidden');
        
        const route = this.data.find(r => r.id === routeId);
        document.getElementById('current-route-name').textContent = route.name;
        this.dirList.innerHTML = '';

        if (!route.directions || route.directions.length === 0) {
            this.dirList.innerHTML = '<div class="empty">No directions yet</div>';
            return;
        }

        route.directions.forEach(d => {
            const el = document.createElement('div');
            el.className = `admin-item ${this.currentDirId === d.id ? 'active' : ''}`;
            el.innerHTML = `
                <div>
                    <strong>${d.description}</strong> <span class="badge">${d.day_type}</span>
                </div>
                <div class="actions">
                    <button class="btn-text btn-edit" data-id="${d.id}">Edit</button>
                    <button class="btn-text btn-del" data-id="${d.id}">Del</button>
                </div>
            `;
            
            el.addEventListener('click', (e) => {
                if (e.target.tagName !== 'BUTTON') {
                    this.currentDirId = d.id;
                    this.renderDirections(routeId);
                    this.renderDepartures(d.id);
                }
            });

            el.querySelector('.btn-edit').addEventListener('click', () => this.showModal('direction', d));
            el.querySelector('.btn-del').addEventListener('click', () => this.deleteEntity('directions', d.id));

            this.dirList.appendChild(el);
        });
    }

    renderDepartures(dirId) {
        this.depSection.classList.remove('hidden');
        
        const route = this.data.find(r => r.id === this.currentRouteId);
        const dir = route.directions.find(d => d.id === dirId);
        document.getElementById('current-dir-name').textContent = dir.description;
        
        this.depList.innerHTML = '';

        if (!dir.departures || dir.departures.length === 0) {
            this.depList.innerHTML = '<div class="empty">No departures yet</div>';
            return;
        }

        // Sort departures by time
        const sortedDeps = [...dir.departures].sort((a, b) => a.time.localeCompare(b.time));

        sortedDeps.forEach(dep => {
            const el = document.createElement('div');
            el.className = 't-btn';
            el.innerHTML = `${dep.time}<sup>${dep.note_symbol || ''}</sup>`;
            
            // Allow deleting on click
            el.addEventListener('click', () => {
                if(confirm(`Delete departure ${dep.time}?`)) {
                    this.deleteEntity('departures', dep.id);
                }
            });
            this.depList.appendChild(el);
        });
    }

    showModal(type, entity = null) {
        this.modalType = type;
        this.modalEntityId = entity ? entity.id : null;
        
        let html = '';
        if (type === 'bulk') {
            this.modalTitle.textContent = 'Bulk Import from Text';
            html = `
                <label>Provider (e.g. manual, intercity, osypa)</label>
                <input type="text" id="m-provider" value="manual" required>
                <label>Route Name (e.g. Nicosia ↔ Limassol)</label>
                <input type="text" id="m-name" required>
                <label>Paste Raw Schedule Text</label>
                <textarea id="m-text" rows="15" required style="width:100%; background:rgba(255,255,255,0.05); color:white; border:1px solid #4f46e5; padding:10px; border-radius:8px; font-family:inherit;"></textarea>
            `;
        } else if (type === 'route') {
            this.modalTitle.textContent = entity ? 'Edit Route' : 'New Route';
            html = `
                <label>Provider (e.g. manual, intercity, osypa)</label>
                <input type="text" id="m-provider" value="${entity ? entity.provider : 'manual'}" required>
                <label>Name</label>
                <input type="text" id="m-name" value="${entity ? entity.name : ''}" required>
                <label>URL</label>
                <input type="text" id="m-url" value="${entity && entity.url ? entity.url : ''}">
            `;
        } else if (type === 'direction') {
            this.modalTitle.textContent = entity ? 'Edit Direction' : 'New Direction';
            html = `
                <label>Description (e.g. Paphos -> City)</label>
                <input type="text" id="m-desc" value="${entity ? entity.description : ''}" required>
                <label>Day Type (e.g. all, weekday, weekend)</label>
                <input type="text" id="m-day" value="${entity ? entity.day_type : 'all'}" required>
            `;
        } else if (type === 'departure') {
            this.modalTitle.textContent = 'New Departure';
            html = `
                <label>Time (HH:MM)</label>
                <input type="text" id="m-time" required placeholder="08:00">
                <label>Note Symbol (optional, e.g. *)</label>
                <input type="text" id="m-sym">
                <label>Note Text (optional)</label>
                <input type="text" id="m-txt">
            `;
        }

        this.modalFields.innerHTML = html;
        this.modal.classList.add('show');
    }

    closeModal() {
        this.modal.classList.remove('show');
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        let url = `/api/admin/${this.modalType}s`;
        let method = 'POST';
        if (this.modalEntityId) {
            url += `/${this.modalEntityId}`;
            method = 'PUT';
        }

        let payload = {};
        if (this.modalType === 'bulk') {
            url = '/api/admin/routes/bulk';
            method = 'POST';
            payload = {
                provider: document.getElementById('m-provider').value,
                name: document.getElementById('m-name').value,
                text: document.getElementById('m-text').value
            };
        } else if (this.modalType === 'route') {
            payload = {
                provider: document.getElementById('m-provider').value,
                name: document.getElementById('m-name').value,
                url: document.getElementById('m-url').value || null
            };
        } else if (this.modalType === 'direction') {
            payload = {
                route_id: this.currentRouteId,
                description: document.getElementById('m-desc').value,
                day_type: document.getElementById('m-day').value
            };
            if (method === 'PUT') delete payload.route_id; // don't update foreign key
        } else if (this.modalType === 'departure') {
            payload = {
                direction_id: this.currentDirId,
                time: document.getElementById('m-time').value,
                note_symbol: document.getElementById('m-sym').value || null,
                note_text: document.getElementById('m-txt').value || null
            };
            if (method === 'PUT') delete payload.direction_id;
        }

        try {
            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                this.closeModal();
                this.load(); // Refresh data
            } else {
                const data = await res.json();
                alert('Error: ' + JSON.stringify(data));
            }
        } catch(e) {
            alert('Network error');
        }
    }

    async deleteEntity(type, id) {
        if (!confirm('Are you sure you want to delete this?')) return;
        
        try {
            const res = await fetch(`/api/admin/${type}/${id}`, { method: 'DELETE' });
            if (res.ok) {
                if (type === 'routes' && this.currentRouteId === id) this.currentRouteId = null;
                if (type === 'directions' && this.currentDirId === id) this.currentDirId = null;
                this.load();
            } else {
                alert('Error deleting');
            }
        } catch(e) {
            console.error(e);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new AdminApp();
    app.load();
});
