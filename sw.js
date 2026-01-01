// Service Worker - Offline desteği ve caching
const CACHE_NAME = 'hosgoru-v6';
const urlsToCache = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/database.xlsx',
  '/manifest.json'
];

// Kurulum sırasında cache'e dosyaları ekle
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache açıldı ve dosyalar eklendi');
        return cache.addAll(urlsToCache).catch(err => {
          console.warn('Bazı dosyalar cache'lenmedi:', err);
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
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Başarılı response'u cache'le
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
              return response || new Response('Çevrimdışı moddasınız. Lütfen internet bağlantısını kontrol edin.', {
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

// Push notifications desteği (opsiyonel)
self.addEventListener('push', event => {
  const data = event.data.json();
  const options = {
    body: data.body || 'Yeni bir güncellemesi var!',
    icon: '/data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%231e3c72" width="192" height="192"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="80" fill="white" font-weight="bold">TA</text></svg>',
    badge: '/data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><circle cx="48" cy="48" r="45" fill="%231e3c72"/></svg>'
  };
  event.waitUntil(self.registration.showNotification('Turnuva Analizi', options));
});

console.log('Service Worker aktif edildi');
