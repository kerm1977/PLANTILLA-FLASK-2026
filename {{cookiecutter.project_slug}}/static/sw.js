const CACHE_NAME = 'flask-pwa-v1';
const URLS_TO_CACHE = [
  '/',
  '/movil',
  '/static/manifest.json',
  '/static/css/styles.css',
  '/static/js/main.js',
  '/static/js/pwa.js',
  '/static/icons/icon.svg',
  '/static/vendor/bootstrap/css/bootstrap.min.css',
  '/static/vendor/bootstrap/js/bootstrap.bundle.min.js',
  '/static/vendor/bootstrap-icons/bootstrap-icons.min.css'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    })
  );
});
