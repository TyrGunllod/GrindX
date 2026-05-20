# Visual Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement self-hosted favicon (diamond+GX) and self-hosted fonts (Barlow Condensed, DM Sans) for GrindX frontend.

**Architecture:** Create SVG source for favicon, generate all required formats (ICO, PNG, mask-icon), download font .woff2 files from @fontsource, replace CDN @import with local @font-face in core.css, and add favicon meta tags to all HTML entry points.

**Tech Stack:** SVG, PNG, ICO, CSS @font-face, HTML link/manifest tags, Python (script for favicon generation)

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `packages/frontend-webapp/assets/favicon.svg` | Create | SVG source for favicon (diamond + GX) |
| `packages/frontend-webapp/assets/favicon.ico` | Create | Multi-size ICO (16×16, 32×32) |
| `packages/frontend-webapp/assets/favicon-32.png` | Create | 32×32 PNG favicon |
| `packages/frontend-webapp/assets/apple-touch-icon.png` | Create | 180×180 PNG for iOS |
| `packages/frontend-webapp/assets/mask-icon.svg` | Create | Monochrome SVG for Safari pinned tab |
| `packages/frontend-webapp/assets/site.webmanifest` | Create | PWA manifest with app name, colors, icons |
| `packages/frontend-webapp/shared/fonts/barlow-condensed-400.woff2` | Create | Barlow Condensed Regular |
| `packages/frontend-webapp/shared/fonts/barlow-condensed-700.woff2` | Create | Barlow Condensed Bold |
| `packages/frontend-webapp/shared/fonts/dm-sans-400.woff2` | Create | DM Sans Regular |
| `packages/frontend-webapp/shared/fonts/dm-sans-500.woff2` | Create | DM Sans Medium |
| `packages/frontend-webapp/shared/fonts/dm-sans-700.woff2` | Create | DM Sans Bold |
| `packages/frontend-webapp/shared/core.css` | Modify | Replace CDN @import with local @font-face |
| `packages/frontend-webapp/index.html` | Modify | Add favicon meta tags |
| `packages/frontend-webapp/dashboard.html` | Modify | Add favicon meta tags |

---

### Task 1: Generate Favicon SVG Source

**Files:**
- Create: `packages/frontend-webapp/assets/favicon.svg`

- [ ] **Step 1: Create assets directory and favicon.svg**

Create the directory and the SVG source file with the diamond + GX design:

```bash
New-Item -ItemType Directory -Force -Path "D:\_Projetos\GrindX\packages\frontend-webapp\assets"
```

```xml
<!-- packages/frontend-webapp/assets/favicon.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="12" fill="#0f172a"/>
  <polygon points="32,8 56,32 32,56 8,32" fill="none" stroke="#00c2e0" stroke-width="3"/>
  <text x="32" y="40" text-anchor="middle" font-family="'Barlow Condensed', Arial, sans-serif" font-size="20" font-weight="700" fill="#00c2e0">GX</text>
</svg>
```

- [ ] **Step 2: Commit**

```bash
git add packages/frontend-webapp/assets/favicon.svg
git commit -m "feat: add favicon SVG source (diamond + GX)"
```

---

### Task 2: Generate Favicon PNG and ICO Files

**Files:**
- Create: `packages/frontend-webapp/assets/favicon.ico`
- Create: `packages/frontend-webapp/assets/favicon-32.png`
- Create: `packages/frontend-webapp/assets/apple-touch-icon.png`

- [ ] **Step 1: Create Python script to convert SVG to PNG/ICO**

Create a conversion script that uses the `svglib` + `reportlab` or `Pillow` libraries. Since these may not be installed, use a pure Python approach with `cairosvg` if available, or generate PNGs programmatically.

```bash
cd D:\_Projetos\GrindX && pip install cairosvg pillow 2>$null; if ($LASTEXITCODE -ne 0) { Write-Output "Will use alternative method" }
```

- [ ] **Step 2: Create the conversion script**

```python
# scripts/generate_favicon.py
"""Generate favicon PNG/ICO files from SVG source."""
import os
import struct
import zlib

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "packages", "frontend-webapp", "assets")
SVG_SOURCE = os.path.join(ASSETS_DIR, "favicon.svg")

SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
  <rect width="64" height="64" rx="12" fill="#0f172a"/>
  <polygon points="32,8 56,32 32,56 8,32" fill="none" stroke="#00c2e0" stroke-width="3"/>
  <text x="32" y="40" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#00c2e0">GX</text>
</svg>"""


def svg_to_png_cairo(svg_content, output_path, size):
    """Convert SVG to PNG using cairosvg."""
    scaled_svg = svg_content.format(size=size)
    cairosvg.svg2png(bytestring=scaled_svg.encode(), write_to=output_path, output_width=size, output_height=size)


def create_png_with_pillow(output_path, size):
    """Create a simple PNG fallback using Pillow with the diamond+GX design."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not available, skipping PNG generation")
        return False

    img = Image.new("RGBA", (size, size), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Rounded rect approximation (draw rect)
    margin = 2
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=size * 0.19, fill=(15, 23, 42, 255))

    # Diamond shape
    cx, cy = size // 2, size // 2
    d = size * 0.38
    diamond = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
    draw.polygon(diamond, outline=(0, 194, 224, 255), width=max(2, size // 21))

    # GX text
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.32))
    except (IOError, OSError):
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), "GX", font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_x = (size - text_w) // 2
    text_y = int(size * 0.62)
    draw.text((text_x, text_y), "GX", fill=(0, 194, 224, 255), font=font)

    img.save(output_path, "PNG")
    return True


def create_ico(png_16_path, png_32_path, output_path):
    """Create a multi-size .ico file from PNG images."""
    with open(png_16_path, "rb") as f16:
        data16 = f16.read()
    with open(png_32_path, "rb") as f32:
        data32 = f32.read()

    # ICO header: 2 images
    header = struct.pack("<HHH", 1, 1, 2)

    # Directory entries
    entries = b""
    offsets = []
    current_offset = 6 + 16 * 2  # header + 2 directory entries

    for i, (data, w, h) in enumerate([(data16, 16, 16), (data32, 32, 32)]):
        entries += struct.pack("<BBBBHHII",
            w if w < 256 else 0,
            h if h < 256 else 0,
            0,  # color palette
            0,  # reserved
            1,  # color planes
            32, # bits per pixel
            len(data),
            current_offset
        )
        offsets.append(data)
        current_offset += len(data)

    with open(output_path, "wb") as f:
        f.write(header + entries)
        for data in offsets:
            f.write(data)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    sizes = {
        "favicon-16.png": 16,
        "favicon-32.png": 32,
        "apple-touch-icon.png": 180,
    }

    for filename, size in sizes.items():
        output_path = os.path.join(ASSETS_DIR, filename)
        print(f"Generating {filename} ({size}x{size})...")

        if HAS_CAIRO:
            svg_to_png_cairo(SVG_CONTENT, output_path, size)
        else:
            success = create_png_with_pillow(output_path, size)
            if not success:
                print(f"  WARNING: Could not generate {filename}")

    # Create ICO from 16 and 32 PNGs
    png_16 = os.path.join(ASSETS_DIR, "favicon-16.png")
    png_32 = os.path.join(ASSETS_DIR, "favicon-32.png")
    ico_path = os.path.join(ASSETS_DIR, "favicon.ico")

    if os.path.exists(png_16) and os.path.exists(png_32):
        print("Generating favicon.ico...")
        create_ico(png_16, png_32, ico_path)
        # Clean up temp PNG
        if os.path.exists(png_16):
            os.remove(png_16)

    print("Done! Generated files:")
    for f in os.listdir(ASSETS_DIR):
        if f.endswith((".png", ".ico")):
            fpath = os.path.join(ASSETS_DIR, f)
            print(f"  {f} ({os.path.getsize(fpath)} bytes)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the conversion script**

```bash
cd D:\_Projetos\GrindX && python scripts/generate_favicon.py
```

Expected output:
```
Generating favicon-16.png (16x16)...
Generating favicon-32.png (32x32)...
Generating apple-touch-icon.png (180x180)...
Generating favicon.ico...
Done! Generated files:
  favicon-32.png (XXX bytes)
  apple-touch-icon.png (XXX bytes)
  favicon.ico (XXX bytes)
```

- [ ] **Step 4: Verify generated files exist**

```bash
Test-Path "D:\_Projetos\GrindX\packages\frontend-webapp\assets\favicon.ico"
Test-Path "D:\_Projetos\GrindX\packages\frontend-webapp\assets\favicon-32.png"
Test-Path "D:\_Projetos\GrindX\packages\frontend-webapp\assets\apple-touch-icon.png"
```

All should return `True`.

- [ ] **Step 5: Commit**

```bash
git add packages/frontend-webapp/assets/favicon.ico packages/frontend-webapp/assets/favicon-32.png packages/frontend-webapp/assets/apple-touch-icon.png scripts/generate_favicon.py
git commit -m "feat: generate favicon ICO and PNG assets from SVG source"
```

---

### Task 3: Create Safari Mask Icon (Monochrome SVG)

**Files:**
- Create: `packages/frontend-webapp/assets/mask-icon.svg`

- [ ] **Step 1: Create mask-icon.svg**

The mask icon must be monochrome (single color fill, no stroke, no background). Safari applies the color via the `color` attribute in the `<link>` tag.

```xml
<!-- packages/frontend-webapp/assets/mask-icon.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <polygon points="32,8 56,32 32,56 8,32" fill="context-fill" stroke="context-stroke" stroke-width="3"/>
  <text x="32" y="40" text-anchor="middle" font-family="'Barlow Condensed', Arial, sans-serif" font-size="20" font-weight="700" fill="context-fill">GX</text>
</svg>
```

Note: `context-fill` and `context-stroke` allow Safari to apply the color from the `<link rel="mask-icon" color="#00c2e0">` tag.

- [ ] **Step 2: Verify SVG is valid**

```bash
Select-String -Path "D:\_Projetos\GrindX\packages\frontend-webapp\assets\mask-icon.svg" -Pattern "context-fill"
```

Should find 2 matches (polygon fill and text fill).

- [ ] **Step 3: Commit**

```bash
git add packages/frontend-webapp/assets/mask-icon.svg
git commit -m "feat: add Safari mask icon (monochrome SVG)"
```

---

### Task 4: Create PWA Manifest

**Files:**
- Create: `packages/frontend-webapp/assets/site.webmanifest`

- [ ] **Step 1: Create site.webmanifest**

```json
{
  "name": "GrindX — Sistema de Gestão Integrado",
  "short_name": "GrindX",
  "description": "ERP modular com arquitetura de monorepo",
  "start_url": "/index.html",
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
      "src": "/apple-touch-icon.png",
      "sizes": "180x180",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

- [ ] **Step 2: Validate JSON**

```bash
Get-Content "D:\_Projetos\GrindX\packages\frontend-webapp\assets\site.webmanifest" | ConvertFrom-Json | Out-Null; if ($?) { Write-Output "Valid JSON" }
```

Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add packages/frontend-webapp/assets/site.webmanifest
git commit -m "feat: add PWA site.webmanifest"
```

---

### Task 5: Download and Install Self-Hosted Fonts

**Files:**
- Create: `packages/frontend-webapp/shared/fonts/barlow-condensed-400.woff2`
- Create: `packages/frontend-webapp/shared/fonts/barlow-condensed-700.woff2`
- Create: `packages/frontend-webapp/shared/fonts/dm-sans-400.woff2`
- Create: `packages/frontend-webapp/shared/fonts/dm-sans-500.woff2`
- Create: `packages/frontend-webapp/shared/fonts/dm-sans-700.woff2`

- [ ] **Step 1: Create fonts directory**

```bash
New-Item -ItemType Directory -Force -Path "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts"
```

- [ ] **Step 2: Download font files from @fontsource CDN**

Download the .woff2 files directly from jsdelivr (same CDN currently used via @import):

```bash
# Barlow Condensed
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/@fontsource/barlow-condensed@5.1.0/files/barlow-condensed-latin-400-normal.woff2" -OutFile "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts\barlow-condensed-400.woff2"

Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/@fontsource/barlow-condensed@5.1.0/files/barlow-condensed-latin-700-normal.woff2" -OutFile "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts\barlow-condensed-700.woff2"

# DM Sans
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/@fontsource/dm-sans@5.1.0/files/dm-sans-latin-400-normal.woff2" -OutFile "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts\dm-sans-400.woff2"

Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/@fontsource/dm-sans@5.1.0/files/dm-sans-latin-500-normal.woff2" -OutFile "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts\dm-sans-500.woff2"

Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/@fontsource/dm-sans@5.1.0/files/dm-sans-latin-700-normal.woff2" -OutFile "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts\dm-sans-700.woff2"
```

- [ ] **Step 3: Verify all font files were downloaded**

```bash
$fonts = @(
    "barlow-condensed-400.woff2",
    "barlow-condensed-700.woff2",
    "dm-sans-400.woff2",
    "dm-sans-500.woff2",
    "dm-sans-700.woff2"
)
$dir = "D:\_Projetos\GrindX\packages\frontend-webapp\shared\fonts"
foreach ($f in $fonts) {
    $path = Join-Path $dir $f
    $exists = Test-Path $path
    $size = if ($exists) { (Get-Item $path).Length } else { 0 }
    Write-Output "$f : $(if($exists){'OK'}else{'MISSING'}) ($size bytes)"
}
```

Expected: All 5 files show `OK` with size > 0.

- [ ] **Step 4: Commit**

```bash
git add packages/frontend-webapp/shared/fonts/
git commit -m "feat: add self-hosted font files (Barlow Condensed, DM Sans)"
```

---

### Task 6: Update core.css with Local @font-face

**Files:**
- Modify: `packages/frontend-webapp/shared/core.css` (lines 6-8, replace @import with @font-face)

- [ ] **Step 1: Read current core.css font imports**

Current lines 6-8:
```css
@import url('https://cdn.jsdelivr.net/npm/@fontsource/barlow-condensed/700.css');
@import url('https://cdn.jsdelivr.net/npm/@fontsource/dm-sans/400.css');
@import url('https://cdn.jsdelivr.net/npm/@fontsource/dm-sans/500.css');
```

- [ ] **Step 2: Replace CDN @import with local @font-face definitions**

Replace lines 6-8 with:

```css
/* ==========================================
   Self-Hosted Fonts (SIL OFL 1.1)
   - Barlow Condensed: Jeremy Tribby
   - DM Sans: Google
   ========================================== */

@font-face {
    font-family: 'Barlow Condensed';
    src: url('./fonts/barlow-condensed-400.woff2?v=1.0.0') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Barlow Condensed';
    src: url('./fonts/barlow-condensed-700.woff2?v=1.0.0') format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'DM Sans';
    src: url('./fonts/dm-sans-400.woff2?v=1.0.0') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'DM Sans';
    src: url('./fonts/dm-sans-500.woff2?v=1.0.0') format('woff2');
    font-weight: 500;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'DM Sans';
    src: url('./fonts/dm-sans-700.woff2?v=1.0.0') format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}
```

- [ ] **Step 3: Verify no CDN references remain**

```bash
Select-String -Path "D:\_Projetos\GrindX\packages\frontend-webapp\shared\core.css" -Pattern "cdn\.jsdelivr|googleapis|@import.*fontsource"
```

Expected: No matches (empty output).

- [ ] **Step 4: Commit**

```bash
git add packages/frontend-webapp/shared/core.css
git commit -m "refactor: replace CDN font imports with local @font-face definitions"
```

---

### Task 7: Add Favicon Meta Tags to HTML Entry Points

**Files:**
- Modify: `packages/frontend-webapp/index.html` (add to `<head>`)
- Modify: `packages/frontend-webapp/dashboard.html` (add to `<head>`)

- [ ] **Step 1: Add favicon meta tags to index.html**

Add the following block inside the `<head>` section of `index.html`, after the `<title>` tag and before the `<link rel="stylesheet">` tags:

```html
    <!-- Favicon & PWA Assets -->
    <link rel="icon" type="image/x-icon" href="assets/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
    <link rel="mask-icon" href="assets/mask-icon.svg" color="#00c2e0">
    <link rel="manifest" href="assets/site.webmanifest">
    <meta name="theme-color" content="#00c2e0">
```

- [ ] **Step 2: Add favicon meta tags to dashboard.html**

Add the same block inside the `<head>` section of `dashboard.html`, after the `<title>` tag and before the Font Awesome `<link>`:

```html
    <!-- Favicon & PWA Assets -->
    <link rel="icon" type="image/x-icon" href="assets/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
    <link rel="mask-icon" href="assets/mask-icon.svg" color="#00c2e0">
    <link rel="manifest" href="assets/site.webmanifest">
    <meta name="theme-color" content="#00c2e0">
```

- [ ] **Step 3: Verify meta tags in both files**

```bash
Select-String -Path "D:\_Projetos\GrindX\packages\frontend-webapp\index.html","D:\_Projetos\GrindX\packages\frontend-webapp\dashboard.html" -Pattern "favicon\.ico|mask-icon|site\.webmanifest"
```

Expected: Both files should show matches for `favicon.ico`, `mask-icon`, and `site.webmanifest`.

- [ ] **Step 4: Commit**

```bash
git add packages/frontend-webapp/index.html packages/frontend-webapp/dashboard.html
git commit -m "feat: add favicon meta tags to HTML entry points"
```

---

### Task 8: Verification and Cleanup

**Files:**
- Verify: All assets load correctly
- Verify: No external font requests

- [ ] **Step 1: Verify no external CDN requests remain**

```bash
Select-String -Path "D:\_Projetos\GrindX\packages\frontend-webapp\shared\core.css" -Pattern "jsdelivr|googleapis|@import"
```

Expected: No matches.

- [ ] **Step 2: Verify all asset files exist**

```bash
$assets = @(
    "packages/frontend-webapp/assets/favicon.ico",
    "packages/frontend-webapp/assets/favicon-32.png",
    "packages/frontend-webapp/assets/apple-touch-icon.png",
    "packages/frontend-webapp/assets/mask-icon.svg",
    "packages/frontend-webapp/assets/site.webmanifest",
    "packages/frontend-webapp/shared/fonts/barlow-condensed-400.woff2",
    "packages/frontend-webapp/shared/fonts/barlow-condensed-700.woff2",
    "packages/frontend-webapp/shared/fonts/dm-sans-400.woff2",
    "packages/frontend-webapp/shared/fonts/dm-sans-500.woff2",
    "packages/frontend-webapp/shared/fonts/dm-sans-700.woff2"
)
$root = "D:\_Projetos\GrindX"
$allOk = $true
foreach ($a in $assets) {
    $path = Join-Path $root $a
    $exists = Test-Path $path
    if (-not $exists) { $allOk = $false }
    $size = if ($exists) { (Get-Item $path).Length } else { 0 }
    Write-Output "$a : $(if($exists){'OK'}else{'MISSING'}) ($size bytes)"
}
if ($allOk) { Write-Output "ALL ASSETS OK" } else { Write-Output "SOME ASSETS MISSING" }
```

Expected: All files show `OK` with size > 0, final line: `ALL ASSETS OK`.

- [ ] **Step 3: Start local server and verify visually**

```bash
python -m http.server 5500 --directory "D:\_Projetos\GrindX\packages\frontend-webapp"
```

Open `http://localhost:5500` in browser and verify:
- Favicon appears in browser tab
- Fonts render correctly (Barlow Condensed for GRINDX logo, DM Sans for body text)
- No console errors related to fonts or favicon

- [ ] **Step 4: Final commit — mark visual assets complete**

```bash
git status
git add -A
git commit -m "feat: complete visual assets (favicon + self-hosted fonts)

- Favicon: diamond+GX design (ICO, PNG, mask-icon, manifest)
- Fonts: Barlow Condensed 400/700, DM Sans 400/500/700 (self-hosted)
- Removed CDN font dependencies
- Added PWA support (site.webmanifest, apple-touch-icon)
- Safari pinned tab support (mask-icon.svg)"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** All spec requirements mapped to tasks:
  - Favicon SVG source → Task 1
  - Favicon ICO/PNG → Task 2
  - Mask icon SVG → Task 3
  - PWA manifest → Task 4
  - Font woff2 download → Task 5
  - @font-face in core.css → Task 6
  - HTML meta tags → Task 7
  - Verification → Task 8
- [x] **No placeholders:** All steps contain actual code/commands
- [x] **Type consistency:** File paths consistent across all tasks
- [x] **DRY/YAGNI:** Only required assets created, no extras
- [x] **Frequent commits:** Each task ends with a commit
- [x] **Version query string:** `?v=1.0.0` included in @font-face URLs for cache busting
