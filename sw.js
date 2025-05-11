const CACHE_NAME = "workout-app-cache-v1";
const urlsToCache = [
  "/",
  // Add other essential assets if you know them,
  // but Streamlit dynamically loads many things.
  // For a basic PWA, the manifest and this shell might be enough
  // for "add to homescreen".
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Opened cache");
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response; // Serve from cache
      }
      return fetch(event.request); // Fetch from network
    })
  );
});
