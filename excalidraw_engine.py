#!/usr/bin/env python3
"""
excalidraw_engine.py — Motor de Integración de Diagramas Excalidraw
Soporta diagramas exportados desde Excalidraw en formato SVG (.svg, .excalidraw.svg)
o PNG (.png, .excalidraw.png). Realiza renderizado vectorial con CairoSVG, auto-recorte
de bordes vacíos y renderizado de marco flotante tipo 'blueprint' o tarjeta de arquitectura.
"""

import os
import sys
import io
from PIL import Image, ImageDraw, ImageOps

# Importar site packages de usuario si existen
import site
user_site = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if os.path.exists(user_site):
    site.addsitedir(user_site)

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

def autocrop_image(img: Image.Image, padding: int = 20) -> Image.Image:
    """Recorta el espacio sobrante transparente o blanco alrededor del dibujo."""
    img_rgba = img.convert("RGBA")
    # Obtener bbox basado en canal alfa
    alpha = img_rgba.split()[-1]
    bbox = alpha.getbbox()

    if not bbox:
        # Si no hay canal alfa o es opaca, intentar detectar bordes blancos
        bg = Image.new(img_rgba.mode, img_rgba.size, (255, 255, 255, 255))
        diff = ImageOps.invert(img_rgba.convert("RGB"))
        bbox = diff.getbbox()

    if bbox:
        left, top, right, bottom = bbox
        # Añadir un pequeño padding de cortesía
        w, h = img.size
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(w, right + padding)
        bottom = min(h, bottom + padding)
        return img_rgba.crop((left, top, right, bottom))
    return img_rgba

def load_excalidraw_diagram(diagram_path: str, max_w: int = 960, max_h: int = 560) -> Image.Image:
    """
    Carga y procesa un diagrama de Excalidraw (SVG o PNG) escalándolo de forma nítida.
    """
    if not os.path.exists(diagram_path):
        raise FileNotFoundError(f"Diagrama no encontrado en: {diagram_path}")

    ext = os.path.splitext(diagram_path)[1].lower()

    if ext == ".excalidraw":
        # Archivo JSON bruto de Excalidraw
        raise ValueError(
            f"El archivo '{diagram_path}' es el JSON de Excalidraw.\n"
            "💡 Para máxima nitidez, en Excalidraw pulsa 'Exportar imagen' y guárdalo como SVG o PNG."
        )

    if ext == ".svg":
        if not CAIROSVG_AVAILABLE:
            raise RuntimeError("CairoSVG no está disponible para renderizar SVG. Instala: pip install cairosvg")
        # Renderizamos con supersampling (2x) para nitidez retina
        png_bytes = cairosvg.svg2png(url=diagram_path, scale=2.0)
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    else:
        img = Image.open(diagram_path).convert("RGBA")

    # Recortar márgenes excesivos
    cropped = autocrop_image(img, padding=16)

    # Escalar proporcionalmente al espacio disponible
    cw, ch = cropped.size
    scale = min(max_w / cw, max_h / ch)
    target_w = max(1, int(cw * scale))
    target_h = max(1, int(ch * scale))

    return cropped.resize((target_w, target_h), Image.LANCZOS)

def render_diagram_card(
    base_image: Image.Image,
    diagram_path: str,
    box: tuple[int, int, int, int],
    card_bg: str = "#ffffff",
    card_border: str = "#e2e8f0",
    radius: int = 32,
    theme: str = "light"
) -> tuple[int, int]:
    """
    Dibuja un marco flotante estilizado para diagramas y coloca el diagrama centrado.
    Devuelve las coordenadas del centro del diagrama.
    """
    x1, y1, x2, y2 = box
    bw = x2 - x1
    bh = y2 - y1

    W, H = base_image.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Convertir colores hex
    def to_rgba(h, a=255):
        h = h.lstrip("#")
        p = [int(h[i:i+2], 16) for i in (0, 2, 4)]
        return tuple(p) + (a,)

    # Sombra suave exterior
    shadow_box = [x1 + 4, y1 + 6, x2 + 4, y2 + 10]
    draw.rounded_rectangle(shadow_box, radius=radius, fill=(0, 0, 0, 35))

    # Tarjeta de fondo
    bg_rgba = to_rgba(card_bg, 245) if len(card_bg) <= 7 else to_rgba(card_bg[:7], int(card_bg[7:9], 16))
    border_rgba = to_rgba(card_border, 180)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg_rgba, outline=border_rgba, width=2)

    # Detalle de ventana técnica / botones de terminal en la esquina superior izquierda
    dot_y = y1 + 22
    dot_x = x1 + 25
    draw.ellipse([dot_x, dot_y, dot_x + 10, dot_y + 10], fill=(239, 68, 68, 200)) # rojo
    draw.ellipse([dot_x + 16, dot_y, dot_x + 26, dot_y + 10], fill=(245, 158, 11, 200)) # amarillo
    draw.ellipse([dot_x + 32, dot_y, dot_x + 42, dot_y + 10], fill=(16, 185, 129, 200)) # verde

    # Etiqueta sutil en la esquina superior derecha
    # Se añade la capa de tarjeta a la imagen base
    base_image.alpha_composite(overlay)

    # Cargar y colocar el diagrama dentro del contenedor (dejando espacio para la barra de título)
    pad_horiz = 30
    pad_top = 45
    pad_bottom = 25
    avail_w = bw - pad_horiz * 2
    avail_h = bh - pad_top - pad_bottom

    diag_img = load_excalidraw_diagram(diagram_path, max_w=avail_w, max_h=avail_h)
    dw, dh = diag_img.size

    # Centrar dentro del área disponible
    dx = x1 + pad_horiz + (avail_w - dw) // 2
    dy = y1 + pad_top + (avail_h - dh) // 2

    base_image.paste(diag_img, (dx, dy), diag_img)
    return (dx, dy)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 excalidraw_engine.py <diagrama.svg|png> [--preview salida.png]")
        sys.exit(1)

    path = sys.argv[1]
    diag = load_excalidraw_diagram(path, 800, 500)
    print(f"✅ Diagrama procesado: {diag.size[0]}×{diag.size[1]}px ({diag.mode})")

    if "--preview" in sys.argv:
        idx = sys.argv.index("--preview")
        out = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "preview.png"
        canvas = Image.new("RGBA", (1080, 1080), (15, 23, 42, 255))
        render_diagram_card(canvas, path, (60, 200, 1020, 800))
        canvas.save(out)
        print(f"🖼️  Preview guardada en: {out}")
