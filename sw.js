// Service Worker - Offline support and caching
const CACHE_NAME = 'hosgoru-v12';
const urlsToCache = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/database.xlsx',
  '/manifest.json'
  // Never add database.json here!
];

// Add files to cache during installation
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened and files added');
        return cache.addAll(urlsToCache).catch(err => {
          console.warn('Some files could not be cached:', err);
        });
      })
  );
  self.skipWaiting();
});

// Aktif olmayan eski cache'leri sil
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eski cache siliniyor:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch isteklerini handle et - Network First, Cache Fallback
self.addEventListener('fetch', event => {
  // GET istekleri için network-first stratejisi
  if (event.request.method === 'GET') {
    // JSON files and grid view ASLA cache'lenmesin - her zaman network'ten al
    if (event.request.url.includes('database.json') || 
        event.request.url.includes('database_temp.json') ||
        event.request.url.includes('hands_database.json') ||
        event.request.url.includes('board_results.json') ||
        event.request.url.includes('boards_grid_view.html')) {
      event.respondWith(
        fetch(event.request)
          .catch(() => {
            // Network başarısız olursa eski cache'den al
            return caches.match(event.request).then(response => {
              if (response) return response;
              // Cache'de yoksa boş JSON dön
              return new Response('[]', {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
              });
            });
          })
      );
      return;
    }
    
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Başarılı response'u cache'le (database.json dışında)
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          return response;
        })
        .catch(() => {
          // Network başarısız olursa cache'den al
          return caches.match(event.request)
            .then(response => {
              return response || new Response('You are offline. Please check your internet connection.', {
                status: 503,
                statusText: 'Service Unavailable',
                headers: new Headers({
                  'Content-Type': 'text/plain'
                })
              });
            });
        })
    );
  }
});

// Push notifications support (optional)
self.addEventListener('push', event => {
  const data = event.data.json();
  const options = {
    body: data.body || 'New update available!',
    icon: '/data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%231e3c72" width="192" height="192"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="80" fill="white" font-weight="bold">TA</text></svg>',
    badge: '/data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><circle cx="48" cy="48" r="45" fill="%231e3c72"/></svg>'
  };
  event.waitUntil(self.registration.showNotification('Tournament Analysis', options));
});

console.log('Service Worker activated');
