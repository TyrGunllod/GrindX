# scripts/generate_favicon.py
"""Generate favicon PNG/ICO files from SVG source."""
import os
import struct
import subprocess
import sys


def install_package(package_name):
    """Instala um pacote via pip."""
    print(f"Instalando {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    print(f"{package_name} instalado com sucesso!")


def check_and_install_dependencies():
    """Verifica e instala dependências necessárias."""
    dependencies = {
        "Pillow": "Pillow",
        "cairosvg": "cairosvg",
    }

    for import_name, package_name in dependencies.items():
        try:
            __import__(import_name)
        except ImportError:
            install_package(package_name)


# Verificar e instalar dependências antes de importar
check_and_install_dependencies()

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "apps", "frontend-webapp", "assets")

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

    for _i, (data, w, h) in enumerate([(data16, 16, 16), (data32, 32, 32)]):
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
        # Clean up temp PNGs
        os.remove(png_16)
        os.remove(png_32)

    print("Done! Generated files:")
    for f in os.listdir(ASSETS_DIR):
        if f.endswith((".png", ".ico")):
            fpath = os.path.join(ASSETS_DIR, f)
            print(f"  {f} ({os.path.getsize(fpath)} bytes)")


if __name__ == "__main__":
    main()
