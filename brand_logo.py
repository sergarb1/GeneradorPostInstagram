#!/usr/bin/env python3
"""
brand_logo.py — Gestor Inteligente de Logos de Marca
Procesa logos en formato SVG (vectorial vía CairoSVG) o PNG/WebP (raster con canal alfa).
Ofrece posicionamiento configurable, badge protector de cristal esmerilado (frosted glass)
y extracción automática de la paleta cromática de la marca.
"""

import os
import sys
import io
import colorsys
from PIL import Image, ImageDraw

# Cargar site packages de usuario si están en ~/.local
import site
user_site = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if os.path.exists(user_site):
    site.addsitedir(user_site)

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

def load_logo_image(logo_path: str, target_height: int = 60, max_width: int = 300) -> Image.Image:
    """Carga un logo desde SVG o PNG y lo escala manteniendo proporciones."""
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo no encontrado en: {logo_path}")

    ext = os.path.splitext(logo_path)[1].lower()

    if ext == ".svg":
        if not CAIROSVG_AVAILABLE:
            raise RuntimeError("CairoSVG no está disponible para renderizar SVG. Instala: pip install cairosvg")
        # Escala inicial generosa para supersampling nítido
        png_bytes = cairosvg.svg2png(url=logo_path, output_height=target_height * 3)
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    else:
        img = Image.open(logo_path).convert("RGBA")

    # Escalar proporcionalmente al target_height
    orig_w, orig_h = img.size
    aspect = orig_w / orig_h
    new_h = target_height
    new_w = int(new_h * aspect)

    if new_w > max_width:
        new_w = max_width
        new_h = int(new_w / aspect)

    return img.resize((new_w, new_h), Image.LANCZOS)

def extract_brand_palette(logo_path: str) -> dict:
    """Extrae la paleta cromática dominante y vibrante de un logo de marca."""
    img = load_logo_image(logo_path, target_height=120, max_width=400)
    # Filtrar píxeles transparentes y casi blancos/negros
    pixels = [p for p in img.getdata() if len(p) >= 4 and p[3] > 60]
    
    # Colores por defecto si el logo es monocromo o vacío
    default_palette = {
        "primary": "#4f46e5",
        "primary_dark": "#1e1b4b",
        "gradient_top": "#4f46e5",
        "gradient_bottom": "#0f172a",
        "accent_light": "#a5b4fc",
        "card_bg": "#ffffffeb"
    }

    if not pixels:
        return default_palette

    # Reducción de color sobre RGBA
    q = img.quantize(colors=12, method=Image.Quantize.FASTOCTREE)
    palette = q.getpalette()[:36]
    colors = [(palette[i], palette[i+1], palette[i+2]) for i in range(0, len(palette), 3)]

    # Filtrar colores extremos (blanco puro o negro puro)
    vibrant_candidates = []
    for c in colors:
        h, s, v = colorsys.rgb_to_hsv(c[0]/255.0, c[1]/255.0, c[2]/255.0)
        # Nos interesan colores con saturación y brillo moderado/alto
        if s > 0.18 and 0.15 < v < 0.95:
            vibrant_candidates.append((c, s, v))

    if not vibrant_candidates:
        # Si el logo es negro/blanco puro
        return {
            "primary": "#0f172a",
            "primary_dark": "#020617",
            "gradient_top": "#1e293b",
            "gradient_bottom": "#090d16",
            "accent_light": "#94a3b8",
            "card_bg": "#ffffffeb"
        }

    # Seleccionar el color más saturado / icónico
    best_rgb, s, v = max(vibrant_candidates, key=lambda item: item[1] * 0.7 + item[2] * 0.3)
    primary_hex = "#{:02x}{:02x}{:02x}".format(*best_rgb)

    # Derivar tonos complementarios y análogos
    h, s, v = colorsys.rgb_to_hsv(best_rgb[0]/255.0, best_rgb[1]/255.0, best_rgb[2]/255.0)

    # Tono oscuro para fondos o textos
    dark_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(h, min(1.0, s * 1.2), max(0.08, v * 0.35))]
    dark_hex = "#{:02x}{:02x}{:02x}".format(*dark_rgb)

    # Tono muy oscuro para base del gradiente
    deep_dark_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(h, min(1.0, s * 1.3), 0.12)]
    deep_dark_hex = "#{:02x}{:02x}{:02x}".format(*deep_dark_rgb)

    # Acento pastel/claro
    accent_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(h, max(0.15, s * 0.35), 0.95)]
    accent_hex = "#{:02x}{:02x}{:02x}".format(*accent_rgb)

    return {
        "primary": primary_hex,
        "primary_dark": dark_hex,
        "gradient_top": primary_hex,
        "gradient_bottom": deep_dark_hex,
        "accent_light": accent_hex,
        "card_bg": "#ffffffeb"
    }

def render_brand_logo(
    base_image: Image.Image,
    logo_path: str,
    position: str = "top-right",
    height: int = 55,
    margin_x: int = 60,
    margin_y: int = 60,
    badge: bool = False
) -> None:
    """
    Superpone el logo de marca en la imagen base respetando márgenes y aspecto.
    Si badge=True, añade una pastilla de cristal esmerilado detrás para garantizar visibilidad.
    """
    if not logo_path or not os.path.exists(logo_path):
        return

    W, H = base_image.size
    logo = load_logo_image(logo_path, target_height=height)
    lw, lh = logo.size

    # Calcular coordenadas según la posición elegida
    if position == "top-left":
        lx = margin_x
        ly = margin_y
    elif position == "top-right":
        lx = W - margin_x - lw
        ly = margin_y
    elif position == "bottom-left":
        lx = margin_x
        ly = H - margin_y - lh
    elif position == "bottom-right":
        lx = W - margin_x - lw
        ly = H - margin_y - lh
    elif position == "center-top":
        lx = (W - lw) // 2
        ly = margin_y
    else: # default top-right
        lx = W - margin_x - lw
        ly = margin_y

    # Si se pide badge protector (frosted glass pill)
    if badge:
        pad_x = 18
        pad_y = 10
        badge_box = [lx - pad_x, ly - pad_y, lx + lw + pad_x, ly + lh + pad_y]
        badge_radius = (lh + pad_y * 2) // 2

        # Crear capa semi-transparente
        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_b = ImageDraw.Draw(badge_layer)
        # Relleno blanco con 80% opacidad o vidrio oscuro según preferencia
        draw_b.rounded_rectangle(badge_box, radius=badge_radius, fill=(255, 255, 255, 210), outline=(255, 255, 255, 240), width=1)
        base_image.alpha_composite(badge_layer)

    # Pegar el logo en el lienzo
    base_image.paste(logo, (lx, ly), logo)

def setup_brand_template(logo_path: str, template_name: str = "Mi Marca") -> str:
    """
    Crea la plantilla de marca persistente en custom/brand_template.yaml
    extrayendo la paleta de colores y configurando el logo.
    """
    import shutil
    import yaml

    root = os.path.dirname(os.path.abspath(__file__))
    custom_dir = os.path.join(root, "custom")
    os.makedirs(custom_dir, exist_ok=True)

    # Si el logo no está en custom/, copiarlo
    ext = os.path.splitext(logo_path)[1].lower()
    dest_logo_name = f"logo{ext}"
    dest_logo_path = os.path.join(custom_dir, dest_logo_name)
    
    if os.path.abspath(logo_path) != os.path.abspath(dest_logo_path):
        shutil.copy2(logo_path, dest_logo_path)
        rel_logo_path = f"custom/{dest_logo_name}"
    else:
        rel_logo_path = os.path.relpath(dest_logo_path, root)

    # Extraer paleta
    palette = extract_brand_palette(dest_logo_path)

    template_data = {
        "brand_name": template_name,
        "logo": {
            "path": rel_logo_path,
            "position": "top-right",
            "height": 55,
            "badge": True,
            "extract_palette": False
        },
        "colors": {
            "primary": palette["primary"],
            "primary_dark": palette["primary_dark"],
            "gradient_top": palette["gradient_top"],
            "gradient_bottom": palette["gradient_bottom"],
            "accent_light": palette["accent_light"],
            "card_bg": palette.get("card_bg", "#ffffffeb"),
            "text_body": "#334155",
            "text_light": "#64748b"
        },
        "fonts": {
            "title": "Outfit-Bold.ttf",
            "tagline": "Outfit-Regular.ttf",
            "body": "Outfit-Regular.ttf",
            "bold": "Outfit-Bold.ttf"
        }
    }

    out_file = os.path.join(custom_dir, "brand_template.yaml")
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(template_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print("=" * 60)
    print("🏷️  PLANTILLA DE MARCA CONFIGURADA")
    print("=" * 60)
    print(f"✅ Logo guardado en: {rel_logo_path}")
    print(f"🎨 Paleta corporativa extraída:")
    print(f"   • Primario:      {palette['primary']}")
    print(f"   • Oscuro:        {palette['primary_dark']}")
    print(f"   • Acento pastel: {palette['accent_light']}")
    print(f"   • Degradado:     {palette['gradient_top']} → {palette['gradient_bottom']}")
    print(f"💾 Plantilla persistente guardada en: custom/brand_template.yaml")
    print("💡 A partir de ahora, cualquier post que generes adoptará esta identidad.")
    print("=" * 60)
    return out_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 brand_logo.py <logo.svg|png> --setup-template [nombre]")
        print("  python3 brand_logo.py <logo.svg|png> --palette")
        sys.exit(1)

    path = sys.argv[1]
    if "--setup-template" in sys.argv:
        idx = sys.argv.index("--setup-template")
        name = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "Mi Marca"
        setup_brand_template(path, name)
    elif "--palette" in sys.argv:
        pal = extract_brand_palette(path)
        print("🎨 Paleta de marca extraída:")
        for k, v in pal.items():
            print(f"  {k}: {v}")
    else:
        img = load_logo_image(path, target_height=80)
        print(f"✅ Logo cargado correctamente: {img.size[0]}×{img.size[1]}px ({img.mode})")
