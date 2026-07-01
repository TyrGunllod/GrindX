const CACHE = 'grindx-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/dashboard.html',
    '/shared/core.css',
    '/dashboard.css',
    '/style.css',
    '/shared/config.js',
    '/shared/app.js',
    '/shared/apiService.js',
    '/shared/baseController.js',
    '/shared/validation.js',
    '/shared/skinLoader.js',
    '/shared/components/LoadingSpinner.js',
    '/shared/components/ReusableModal.js',
    '/shared/components/FormField.js',
    '/assets/site.webmanifest',
    '/assets/icon-192.png',
    '/assets/icon-512.png',
    '/assets/favicon.ico',
    '/assets/favicon.svg',
    '/assets/favicon.png',
    '/assets/favicon-32.png',
    '/assets/favicon-16.png',
    '/assets/apple-touch-icon.png',
    '/assets/mask-icon.svg',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
        ))
    );
});

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    if (STATIC_ASSETS.includes(url.pathname)) {
        event.respondWith(
            caches.match(request).then((cached) => cached || fetch(request))
        );
        return;
    }

    event.respondWith(
        fetch(request)
            .then((response) => {
                const clone = response.clone();
                caches.open(CACHE).then((cache) => cache.put(request, clone));
                return response;
            })
            .catch(() => caches.match(request))
    );
});
