#!/usr/bin/env python3
"""
stock.py — Gestor de Bancos de Imágenes Libres
Descarga imágenes libres de derechos de Openverse (Creative Commons / Dominio Público),
Wikimedia Commons y URLs directas. Aplica recorte inteligente y capas de contraste (scrim)
para garantizar legibilidad tipográfica sin perder calidad fotográfica.
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT, "custom", "stock_cache")

USER_AGENT = "GeneradorPostInstagram/2.0 (Open-Source Instagram Generator; https://github.com/sergarb1/GeneradorPostInstagram)"

def search_openverse(query: str, per_page: int = 5) -> list[dict]:
    """Busca imágenes libres en la API pública de Openverse (WordPress Foundation)."""
    encoded_query = urllib.parse.quote_plus(query)
    # Buscamos licencias CC comerciales o de dominio público / modificación libre
    url = f"https://api.openverse.org/v1/images/?q={encoded_query}&page_size={per_page}&license_type=commercial,modification"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for item in data.get("results", []):
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title", "Sin título"),
                    "url": item.get("url"),
                    "creator": item.get("creator", "Desconocido"),
                    "license": item.get("license", "CC"),
                    "foreign_landing_url": item.get("foreign_landing_url", "")
                })
            return results
    except Exception as e:
        print(f"⚠️  Error buscando en Openverse: {e}", file=sys.stderr)
        return []

def search_wikimedia(query: str, per_page: int = 5) -> list[dict]:
    """Busca imágenes en Wikimedia Commons a través de su API abierta."""
    encoded_query = urllib.parse.quote_plus(query)
    url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
        f"&gsrnamespace=6&gsrsearch={encoded_query}&gsrlimit={per_page}"
        f"&prop=imageinfo&iiprop=url|extmetadata&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            results = []
            for _, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                img_url = info.get("url")
                if img_url and any(img_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    results.append({
                        "id": str(page.get("pageid")),
                        "title": page.get("title", "").replace("File:", ""),
                        "url": img_url,
                        "creator": "Wikimedia Commons",
                        "license": "Public Domain / CC",
                        "foreign_landing_url": info.get("descriptionurl", "")
                    })
            return results
    except Exception as e:
        print(f"⚠️  Error buscando en Wikimedia: {e}", file=sys.stderr)
        return []

def download_image(image_url: str, cache_dir: str = CACHE_DIR) -> str:
    """Descarga una imagen y la guarda en la caché local."""
    os.makedirs(cache_dir, exist_ok=True)
    url_hash = hashlib.md5(image_url.encode("utf-8")).hexdigest()[:12]
    ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
    if not ext or len(ext) > 5:
        ext = ".jpg"
    cache_path = os.path.join(cache_dir, f"stock_{url_hash}{ext}")

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 1024:
        return cache_path

    req = urllib.request.Request(image_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        with open(cache_path, "wb") as f:
            f.write(content)
    return cache_path

def smart_crop_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Recorte centrado inteligente para ajustar al aspecto exacto sin deformar."""
    orig_w, orig_h = img.size
    target_aspect = target_w / target_h
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        # La imagen original es más ancha: recortamos por los laterales
        new_w = int(orig_h * target_aspect)
        left = (orig_w - new_w) // 2
        img_cropped = img.crop((left, 0, left + new_w, orig_h))
    else:
        # La imagen original es más alta: recortamos arriba/abajo
        new_h = int(orig_w / target_aspect)
        top = (orig_h - new_h) // 2
        img_cropped = img.crop((0, top, orig_w, top + new_h))

    return img_cropped.resize((target_w, target_h), Image.LANCZOS)

def apply_scrim_overlay(img: Image.Image, mode: str = "dark", blur: int = 0) -> Image.Image:
    """
    Aplica una capa de contraste (scrim) para garantizar legibilidad.
    - 'dark': oscurece con viñeta y gradiente vertical suave para texto blanco.
    - 'light': capa lechosa para texto oscuro.
    - 'tint': tinte sutil neutro.
    - 'none': sin overlay.
    """
    w, h = img.size
    base = img.convert("RGBA")

    if blur > 0:
        base = base.filter(ImageFilter.GaussianBlur(blur))

    if mode == "none":
        return base

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if mode == "dark":
        # Gradiente vertical de oscuro superior a muy oscuro inferior + velo general
        for y in range(h):
            factor = y / h
            alpha = int(140 + factor * 85) # de 140 a 225
            draw.line([(0, y), (w, y)], fill=(10, 15, 25, alpha))
    elif mode == "light":
        for y in range(h):
            factor = y / h
            alpha = int(180 + factor * 50)
            draw.line([(0, y), (w, y)], fill=(255, 255, 255, alpha))
    elif mode == "vignette":
        # Viñeta suave
        for y in range(h):
            alpha = int(130)
            draw.line([(0, y), (w, y)], fill=(5, 5, 10, alpha))

    return Image.alpha_composite(base, overlay)

def fetch_stock_background(query_or_url: str, target_size=(1080, 1080), overlay="dark", blur=0) -> str:
    """Busca o descarga la imagen libre, la procesa y devuelve la ruta al archivo procesado."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
        raw_path = download_image(query_or_url)
    else:
        print(f"🔍 Buscando imágenes libres para: '{query_or_url}'...")
        results = search_openverse(query_or_url, per_page=3)
        if not results:
            print("   (Probando en Wikimedia Commons)...")
            results = search_wikimedia(query_or_url, per_page=3)

        if not results:
            raise RuntimeError(f"No se encontraron imágenes libres para '{query_or_url}'")

        chosen = results[0]
        print(f"📸 Seleccionada: '{chosen['title']}' por {chosen['creator']} ({chosen['license']})")
        raw_path = download_image(chosen["url"])

    # Procesar imagen
    with Image.open(raw_path) as raw_img:
        cropped = smart_crop_resize(raw_img, target_size[0], target_size[1])
        processed = apply_scrim_overlay(cropped, mode=overlay, blur=blur)

    out_name = f"bg_{hashlib.md5(query_or_url.encode()).hexdigest()[:8]}_{target_size[0]}x{target_size[1]}.png"
    out_path = os.path.join(CACHE_DIR, out_name)
    processed.save(out_path, "PNG")
    print(f"✅ Fondo procesado listo: {out_path}")
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 stock.py <'búsqueda'|URL> [--overlay dark|light|none] [--blur 0-10] [--output ruta.png]")
        sys.exit(1)

    query = sys.argv[1]
    overlay_mode = "dark"
    blur_amount = 0
    output_custom = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--overlay" and i + 1 < len(sys.argv):
            overlay_mode = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--blur" and i + 1 < len(sys.argv):
            blur_amount = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_custom = sys.argv[i+1]
            i += 2
        else:
            i += 1

    try:
        bg_path = fetch_stock_background(query, (1080, 1080), overlay_mode, blur_amount)
        if output_custom:
            img = Image.open(bg_path)
            img.save(output_custom)
            print(f"📁 Guardado en destino: {output_custom}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
