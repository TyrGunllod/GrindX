# PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make GrindX frontend a fully installable Progressive Web App with offline-capable service worker.

**Architecture:** Generate missing app icons → update manifest → create service worker (Network First for pages, Cache First for assets) → register in app.js → add iOS meta tags.

**Tech Stack:** Vanilla JS, Cache Storage API, service worker, Python (Pillow) for icon generation.

---

### Task 1: Generate PWA icons (192x192 and 512x512)

**Files:**
- Create: `apps/frontend-webapp/assets/icon-192.png`
- Create: `apps/frontend-webapp/assets/icon-512.png`

- [ ] **Step 1: Generate icons from existing favicon**

Run this Python script to resize the existing favicon-32.png to the required sizes:
```powershell
python -c "
from PIL import Image
import pathlib
src = pathlib.Path('apps/frontend-webapp/assets/favicon-32.png')
img = Image.open(src)
for size in [192, 512]:
    out = src.parent / f'icon-{size}.png'
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(out)
    print(f'Created {out.name} ({size}x{size})')
"
```

Expected output:
```
Created icon-192.png (192x192)
Created icon-512.png (512x512)
```

- [ ] **Step 2: Verify files exist**

Run: `ls apps/frontend-webapp/assets/icon-*.png`
Expected: `icon-192.png` and `icon-512.png` listed

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/assets/icon-192.png apps/frontend-webapp/assets/icon-512.png
git commit -m "feat: add PWA icons 192x192 and 512x512"
```

---

### Task 2: Update manifest.json

**Files:**
- Modify: `apps/frontend-webapp/assets/site.webmanifest`

- [ ] **Step 1: Add 192x192 and 512x512 icons + fix start_url**

Replace the icons array and start_url:

```json
{
  "name": "GrindX — Sistema de Gestão Integrado",
  "short_name": "GrindX",
  "description": "ERP modular com arquitetura de monorepo",
  "start_url": "/dashboard.html",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#00c2e0",
  "icons": [
    {
      "src": "/favicon-32.png",
      "sizes": "32x32",
      "type": "image/png"
    },
    {
      "src": "/assets/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/assets/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/apple-touch-icon.png",
      "sizes": "180x180",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/assets/site.webmanifest
git commit -m "feat: add 192x192 and 512x512 icons to manifest, update start_url"
```

---

### Task 3: Create service worker

**Files:**
- Create: `apps/frontend-webapp/sw.js`

- [ ] **Step 1: Write the service worker**

File `apps/frontend-webapp/sw.js`:

```javascript
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
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/sw.js
git commit -m "feat: add service worker with Network First + Cache First strategies"
```

---

### Task 4: Register service worker + add meta tags

**Files:**
- Modify: `apps/frontend-webapp/shared/app.js`
- Modify: `apps/frontend-webapp/index.html`
- Modify: `apps/frontend-webapp/dashboard.html`

- [ ] **Step 1: Register service worker in app.js**

At the end of `app.js` (before the closing of the IIFE or at the bottom of the file), add:

```javascript
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js');
    });
}
```

- [ ] **Step 2: Add iOS meta tags to index.html**

After line 16 (`<meta name="theme-color" content="#00c2e0">`) in `index.html`, add:
```html
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
```

- [ ] **Step 3: Add iOS meta tags to dashboard.html**

After line 14 (`<meta name="theme-color" content="#00c2e0">`) in `dashboard.html`, add:
```html
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
```

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/shared/app.js apps/frontend-webapp/index.html apps/frontend-webapp/dashboard.html
git commit -m "feat: register service worker and add iOS PWA meta tags"
```

---

### Task 5: Verify and format

- [ ] **Step 1: Run lint**

Run: `ruff check .` (only if Python files were changed — none were)
Expected: No errors (no Python files changed)

- [ ] **Step 2: Test service worker registers**

Serve the frontend and check browser DevTools → Application → Service Workers
Expected: `sw.js` registered and active
