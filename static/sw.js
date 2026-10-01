// =========================================================================
// JARVIS Assistant — Progressive Web App Service Worker (v4.0 Mobile-Ready)
// =========================================================================

const CACHE_NAME = 'jarvis-liquid-glass-v2';
const STATIC_ASSETS = [
    '/',
    '/static/style.css',
    '/static/script.js',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// 1. INSTALACIÓN: Pre-cachear assets críticos del shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-cacheando App Shell...');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// 2. ACTIVACIÓN: Limpiar cachés antiguas y tomar control inmediato
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => {
                    console.log('[ServiceWorker] Eliminando caché obsoleta:', key);
                    return caches.delete(key);
                })
            );
        }).then(() => self.clients.claim())
    );
});

// 3. FETCH: Estrategias diferenciadas por tipo de recurso
self.addEventListener('fetch', (event) => {
    const req = event.request;
    const url = new URL(req.url);

    // Omitir WebSockets, peticiones no GET, SSE, TTS stream y archivos de audio generados dinámicamente
    if (
        url.protocol.startsWith('ws') ||
        req.method !== 'GET' ||
        url.pathname.startsWith('/api/tts/stream') ||
        url.pathname.includes('/stream') ||
        url.pathname.startsWith('/static/audio/') ||
        (req.headers.get('Accept') && req.headers.get('Accept').includes('text/event-stream'))
    ) {
        return;
    }

    // Estrategia Network-First para endpoints REST /api/*
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(req)
                .then((networkResponse) => {
                    return networkResponse;
                })
                .catch(async () => {
                    const cachedResponse = await caches.match(req);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return new Response(
                        JSON.stringify({
                            ok: false,
                            data: null,
                            error: { code: 'OFFLINE', message: 'Sin conexión a la red' }
                        }),
                        {
                            status: 503,
                            headers: { 'Content-Type': 'application/json' }
                        }
                    );
                })
        );
        return;
    }

    // Estrategia Cache-First (con network fallback) para assets estáticos (CSS, JS, imágenes, fuentes)
    event.respondWith(
        caches.match(req).then((cachedResponse) => {
            if (cachedResponse) {
                // Actualización en background (stale-while-revalidate)
                fetch(req).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => cache.put(req, networkResponse));
                    }
                }).catch(() => {});
                return cachedResponse;
            }

            return fetch(req).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(req, responseToCache);
                });
                return networkResponse;
            });
        })
    );
});
