/* Service worker: saves every file of the app on the first visit, then serves them without the network. */
"use strict";
importScripts("assets.js");                     // defines ASSET_VERSION and ASSETS (written by build_app.py)
const CACHE = "scicalc-" + ASSET_VERSION;

self.addEventListener("install", function (ev) {
  ev.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (ev) {
  ev.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf("scicalc-") === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (ev) {
  const req = ev.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  ev.respondWith(caches.match(req, { ignoreSearch: true }).then(function (hit) {
    if (hit) return hit;
    return fetch(req).catch(function () {
      if (req.mode === "navigate") return caches.match("index.html");
      return new Response("", { status: 504, statusText: "offline" });
    });
  }));
});
