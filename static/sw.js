const CACHE_NAME = 'cybuses-v5';
const ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/api.js',
    '/static/js/i18n.js',
    '/static/js/components/RouteFinder.js',
    '/static/js/components/BusCard.js',
    '/static/js/components/FilterBar.js',
    '/static/js/components/Modal.js',
    '/static/manifest.json'
];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    // Only intercept HTTP/HTTPS requests
    if (!event.request.url.startsWith('http')) return;

    // For non-GET requests (e.g. POST /api/refresh), pass directly to network
    if (event.request.method !== 'GET') {
        event.respondWith(fetch(event.request));
        return;
    }

    // Network-first strategy with cache fallback for offline PWA support
    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response && response.status === 200) {
                    const resClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, resClone);
                    });
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});

