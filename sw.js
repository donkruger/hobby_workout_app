const CACHE_NAME = "workout-app-cache-v2"; // Incremented version
const OFFLINE_URL = "/offline.html";
const ICON_192 = "/assets/icons/icon-192x192.png"; // Cache the icon

// Add core assets to cache on install
const urlsToCache = [
  "/", // Cache the root/start_url
  OFFLINE_URL,
  ICON_192,
  // Note: We don't cache Streamlit's dynamic JS/CSS here,
  // relying on the browser cache mostly. This focuses on the offline page.
];

// Install event: Open cache and add core assets.
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Opened cache and adding core assets:", urlsToCache);
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting(); // Force the new service worker to activate immediately.
});

// Activate event: Clean up old caches.
self.addEventListener("activate", (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheWhitelist.indexOf(cacheName) === -1) {
              console.log("Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim()) // Take control of open clients.
  );
});

// Fetch event: Handle requests.
self.addEventListener("fetch", (event) => {
  // We only want to handle navigation requests (page loads)
  // with the offline fallback for now.
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => {
        // If the fetch fails (likely offline),
        // return the pre-cached offline page.
        console.log("Fetch failed; serving offline page.");
        return caches.match(OFFLINE_URL);
      })
    );
  } else {
    // For non-navigation requests (assets like JS, CSS, images),
    // try the cache first, then fall back to the network.
    // This isn't perfect for Streamlit's dynamic assets but is a
    // reasonable PWA strategy.
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});
