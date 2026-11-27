#!/usr/bin/env python3
"""
post.py — Motor Central de Generación de Posts para Instagram (v2.0)
Diseñado para trabajar mano a mano con agentes de IA (Antigravity, OpenCode, Freebuff)
y desarrolladores. Soporta:
- Bancos de imágenes libres (Openverse / Wikimedia) con auto-scrim.
- Diagramas técnicos y arquitecturas con Excalidraw (SVG/PNG con CairoSVG).
- Gestión avanzada de logos de marca (SVG/PNG) con extracción de paleta y badge protector.
- Sistema de diseño Anti-IA Slop (tipografía honesta, jerarquía visual y linter).
- Múltiples layouts: card, diagram, minimal, split, quote.
- Formatos: 1:1 (1080×1080), 4:5 Portrait (1080×1350), 9:16 Story (1080×1920).
"""

import os
import sys
import yaml
from PIL import Image, ImageDraw, ImageFont

# Asegurar carga de paquetes locales si están en ~/.local
import site
user_site = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if os.path.exists(user_site):
    site.addsitedir(user_site)

# Módulos auxiliares
try:
    from brand_logo import render_brand_logo, extract_brand_palette
except ImportError:
    render_brand_logo = None
    extract_brand_palette = None

try:
    from stock import fetch_stock_background
except ImportError:
    fetch_stock_background = None

try:
    from excalidraw_engine import render_diagram_card
except ImportError:
    render_diagram_card = None

try:
    from anti_slop import lint_config
except ImportError:
    lint_config = None

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")
CUSTOM_DIR = os.path.join(ROOT, "custom")
OUTPUT_DIR = os.path.join(ROOT, "output")

# Dimensiones estándar según ratio
ASPECT_RATIOS = {
    "1:1": (1080, 1080),
    "square": (1080, 1080),
    "4:5": (1080, 1350),
    "portrait": (1080, 1350),
    "9:16": (1080, 1920),
    "story": (1080, 1920),
}

# Rutas de fuentes del sistema de respaldo
SYSTEM_FONT_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Carga una fuente TTF con sistema de resolución escalonado y robusto."""
    candidates = [
        os.path.join(FONT_DIR, name),
        os.path.join(FONT_DIR, "Outfit-Bold.ttf" if "bold" in name.lower() else "Outfit-Regular.ttf"),
    ] + SYSTEM_FONT_FALLBACKS

    if os.path.isdir(FONT_DIR):
        for f in os.listdir(FONT_DIR):
            if f.endswith(".ttf"):
                candidates.append(os.path.join(FONT_DIR, f))

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()

def hex_to_rgba(h: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Convierte un color hexadecimal (#rgb, #rrggbb o #rrggbbaa) a tupla RGBA."""
    if not h:
        return (255, 255, 255, alpha)
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join([c*2 for c in h])
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    if len(h) >= 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    return (255, 255, 255, alpha)

def draw_gradient(draw: ImageDraw.Draw, w: int, h: int, color_top: str, color_bottom: str):
    """Genera un gradiente vertical de alta fidelidad."""
    top = hex_to_rgba(color_top, 255)
    bot = hex_to_rgba(color_bottom, 255)
    for y in range(h):
        factor = y / h
        r = int(top[0] * (1 - factor) + bot[0] * factor)
        g = int(top[1] * (1 - factor) + bot[1] * factor)
        b = int(top[2] * (1 - factor) + bot[2] * factor)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

def estimate_font_size(text: str, max_w: int, max_h: int, font_name: str, start_size: int = 50, min_size: int = 14) -> int:
    """Calcula el tamaño de fuente óptimo para no desbordar una caja dada."""
    size = start_size
    while size >= min_size:
        font = load_font(font_name, size)
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if tw <= max_w and th <= max_h:
            return size
        size -= 2
    return min_size

def wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Divide un texto en múltiples líneas respetando saltos explícitos y ancho máximo."""
    if not text:
        return []
    lines = text.split("\n")
    result = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        if bbox[2] - bbox[0] <= max_w:
            result.append(line)
        else:
            words = line.split(" ")
            current = ""
            for w in words:
                test = current + (" " if current else "") + w
                tb = draw.textbbox((0, 0), test, font=font)
                if tb[2] - tb[0] <= max_w:
                    current = test
                else:
                    if current:
                        result.append(current)
                    current = w
            if current:
                result.append(current)
    return result

def deep_merge(base: dict, override: dict):
    """Combina diccionarios de configuración recursivamente."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v

def load_config(config_path: str = None) -> dict:
    """Carga config.yaml y combina con configuraciones locales o generadas."""
    main_path = config_path or os.path.join(ROOT, "config.yaml")
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"Configuración no encontrada en: {main_path}")

    with open(main_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Plantilla de marca persistente si existe
    brand_template_path = os.path.join(CUSTOM_DIR, "brand_template.yaml")
    if os.path.exists(brand_template_path):
        with open(brand_template_path, "r", encoding="utf-8") as f:
            bdata = yaml.safe_load(f)
            if bdata:
                deep_merge(cfg, bdata)

    # Overrides opcionales en carpeta custom
    for name in ("config.local.yaml", "config.generated.yaml"):
        path = os.path.join(CUSTOM_DIR, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    deep_merge(cfg, data)

    # Asegurar claves mínimas con valores por defecto
    cfg.setdefault("title", "Título del Post")
    cfg.setdefault("tagline", "Subtítulo descriptivo")
    cfg.setdefault("body", "")
    cfg.setdefault("features", [])
    cfg.setdefault("cta_text", "visita el enlace")
    cfg.setdefault("hashtags", "")
    cfg.setdefault("layout", "card")
    cfg.setdefault("aspect", "1:1")

    colors = cfg.setdefault("colors", {})
    colors.setdefault("primary", "#4f46e5")
    colors.setdefault("primary_dark", "#1e1b4b")
    colors.setdefault("gradient_top", "#312e81")
    colors.setdefault("gradient_bottom", "#0f172a")
    colors.setdefault("card_bg", "#ffffffeb")
    colors.setdefault("text_body", "#334155")
    colors.setdefault("text_light", "#64748b")
    colors.setdefault("accent_light", "#c7d2fe")

    fonts = cfg.setdefault("fonts", {})
    fonts.setdefault("title", "Outfit-Bold.ttf")
    fonts.setdefault("tagline", "Outfit-Regular.ttf")
    fonts.setdefault("body", "Outfit-Regular.ttf")
    fonts.setdefault("bold", "Outfit-Bold.ttf")

    return cfg

# ─────────────────────────────────────────────────────────────
# LAYOUT 1: CARD (Modern Frosted Glass Card)
# ─────────────────────────────────────────────────────────────
def render_card(draw: ImageDraw.Draw, img: Image.Image, cfg: dict, W: int, H: int):
    c = cfg["colors"]
    white = (255, 255, 255, 255)
    accent = hex_to_rgba(c["accent_light"], 255)
    pd = hex_to_rgba(c["primary_dark"], 255)
    prim = hex_to_rgba(c["primary"], 255)

    # ── Header ──
    # Badge de categoría o tema
    badge_topic = cfg.get("category", "DESTACADO").upper()
    badge_font = load_font(cfg["fonts"]["bold"], 14)
    draw.rounded_rectangle([60, 55, 60 + len(badge_topic) * 11 + 24, 85], radius=15, fill=hex_to_rgba(c["primary"], 180))
    draw.text((72, 63), badge_topic, fill=white, font=badge_font)

    # Título principal
    title_fs = estimate_font_size(cfg["title"], W - 180, 70, cfg["fonts"]["title"], 48, 26)
    tf = load_font(cfg["fonts"]["title"], title_fs)
    draw.text((60, 102), cfg["title"], fill=white, font=tf)

    # Tagline
    tag_font = load_font(cfg["fonts"]["tagline"], 22)
    draw.text((60, 168), cfg["tagline"], fill=accent, font=tag_font)

    # ── Tarjeta de Contenido ──
    card_x = 60
    card_y = 220
    card_w = W - 120
    card_h = H - 380 if H > 1080 else 580

    # Capa de cristal con borde sutil
    card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_card = ImageDraw.Draw(card_overlay)

    # Sombra
    draw_card.rounded_rectangle([card_x + 4, card_y + 8, card_x + card_w + 4, card_y + card_h + 12], radius=36, fill=(0, 0, 0, 40))

    # Fondo de tarjeta
    card_bg_color = hex_to_rgba(c.get("card_bg", "#ffffffeb"), 235)
    draw_card.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=36, fill=card_bg_color, outline=(255, 255, 255, 120), width=1)
    img.alpha_composite(card_overlay)

    # ── Cuerpo de texto ──
    by = card_y + 40
    if cfg.get("body"):
        bf = load_font(cfg["fonts"]["body"], 21)
        body_color = hex_to_rgba(c["text_body"], 255)
        lines = wrap_text(draw, cfg["body"], bf, card_w - 70)
        for line in lines[:5]:
            draw.text((card_x + 35, by), line, fill=body_color, font=bf)
            by += 32
        by += 15

    # ── Features / Puntos Clave ──
    features = cfg.get("features", [])
    if features:
        sf = load_font(cfg["fonts"]["bold"], 20)
        df = load_font(cfg["fonts"]["body"], 16)
        pill_font = load_font(cfg["fonts"]["bold"], 14)

        for i, feat in enumerate(features[:4]):
            fy = by + (i * 68)
            if fy + 55 > card_y + card_h:
                break

            # Indicador: símbolo tipográfico o número ordinal limpio anti-slop
            icon = str(feat.get("icon", ""))
            draw.rounded_rectangle([card_x + 35, fy, card_x + 75, fy + 40], radius=12, fill=hex_to_rgba(c["accent_light"], 220))
            
            # Si es un símbolo tipográfico simple compatible (ej: ✓, ★) o alfanumérico corto, usarlo; de lo contrario, usar ordinal elegante 01, 02...
            is_simple_glyph = icon in ("✓", "✔", "★", "✦", "→", "•", "●", "◆") or (icon.isalnum() and len(icon) <= 2)
            if is_simple_glyph:
                draw.text((card_x + 55, fy + 20), icon, fill=pd, font=pill_font, anchor="mm")
            else:
                draw.text((card_x + 55, fy + 20), f"0{i+1}", fill=pd, font=pill_font, anchor="mm")

            draw.text((card_x + 90, fy), feat.get("title", ""), fill=pd, font=sf)
            draw.text((card_x + 90, fy + 26), feat.get("desc", ""), fill=hex_to_rgba(c["text_light"], 255), font=df)

    # ── Botón CTA ──
    cta_y = card_y + card_h + 30
    cta_h = 64
    cta_w = W - 320
    cta_x = (W - cta_w) // 2

    draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=32, fill=white, outline=hex_to_rgba(c["accent_light"], 150), width=1)
    cta_text = cfg.get("cta_text", "")
    cta_font = load_font(cfg["fonts"]["bold"], 22)
    draw.text((W // 2 - 15, cta_y + 18), cta_text, fill=pd, font=cta_font, anchor="mt")
    draw.text((cta_x + cta_w - 45, cta_y + 16), "→", fill=prim, font=cta_font)

    # ── Hashtags / Footer ──
    if cfg.get("hashtags"):
        ht_font = load_font(cfg["fonts"]["tagline"], 15)
        draw.text((W // 2, H - 40), cfg["hashtags"], fill=accent, font=ht_font, anchor="mt")

# ─────────────────────────────────────────────────────────────
# LAYOUT 2: DIAGRAM (Technical / Excalidraw Blueprint Layout)
# ─────────────────────────────────────────────────────────────
def render_diagram_layout(draw: ImageDraw.Draw, img: Image.Image, cfg: dict, W: int, H: int):
    c = cfg["colors"]
    white = (255, 255, 255, 255)
    accent = hex_to_rgba(c["accent_light"], 255)
    pd = hex_to_rgba(c["primary_dark"], 255)

    # Header técnico con Badge
    badge_text = "📐 ARQUITECTURA / DIAGRAMA"
    bf = load_font(cfg["fonts"]["bold"], 13)
    draw.rounded_rectangle([60, 50, 290, 80], radius=15, fill=hex_to_rgba(c["primary"], 200))
    draw.text((75, 58), badge_text, fill=white, font=bf)

    # Título del diagrama
    title_fs = estimate_font_size(cfg["title"], W - 140, 55, cfg["fonts"]["title"], 42, 24)
    tf = load_font(cfg["fonts"]["title"], title_fs)
    draw.text((60, 95), cfg["title"], fill=white, font=tf)

    # Subtítulo explicativo
    sf = load_font(cfg["fonts"]["tagline"], 20)
    draw.text((60, 155), cfg["tagline"], fill=accent, font=sf)

    # Contenedor del Diagrama
    diag_box = (60, 205, W - 60, H - 220)
    diagram_path = cfg.get("diagram", "custom/diagram.svg")

    if os.path.exists(diagram_path) and render_diagram_card:
        render_diagram_card(
            img,
            diagram_path,
            diag_box,
            card_bg=c.get("card_bg", "#ffffff"),
            card_border=c.get("accent_light", "#cbd5e1"),
            radius=28
        )
    else:
        # Placeholder si aún no se ha colocado el diagrama
        draw.rounded_rectangle(diag_box, radius=28, fill=hex_to_rgba(c["card_bg"], 230), outline=(255, 255, 255, 120), width=2)
        warn_f = load_font(cfg["fonts"]["bold"], 24)
        hint_f = load_font(cfg["fonts"]["body"], 18)
        draw.text((W // 2, (diag_box[1] + diag_box[3]) // 2 - 20), "📌 Coloca tu diagrama en:", fill=pd, font=warn_f, anchor="mm")
        draw.text((W // 2, (diag_box[1] + diag_box[3]) // 2 + 20), diagram_path, fill=hex_to_rgba(c["primary"], 255), font=hint_f, anchor="mm")

    # Pie inferior: CTA y hashtags
    cta_box = [60, H - 180, W - 60, H - 110]
    draw.rounded_rectangle(cta_box, radius=20, fill=white)
    cta_font = load_font(cfg["fonts"]["bold"], 20)
    draw.text((85, H - 152), f"💡 {cfg.get('cta_text', '')}", fill=pd, font=cta_font)
    draw.text((W - 100, H - 154), "→", fill=hex_to_rgba(c["primary"], 255), font=cta_font)

    if cfg.get("hashtags"):
        ht_font = load_font(cfg["fonts"]["tagline"], 14)
        draw.text((W // 2, H - 65), cfg["hashtags"], fill=accent, font=ht_font, anchor="mt")

# ─────────────────────────────────────────────────────────────
# LAYOUT 3: MINIMAL (Swiss / Editorial Style)
# ─────────────────────────────────────────────────────────────
def render_minimal(draw: ImageDraw.Draw, img: Image.Image, cfg: dict, W: int, H: int):
    c = cfg["colors"]
    white = (255, 255, 255, 255)
    accent = hex_to_rgba(c["accent_light"], 255)
    prim = hex_to_rgba(c["primary"], 255)

    # Marca sutil superior
    topic = cfg.get("category", "PERSPECTIVA").upper()
    top_f = load_font(cfg["fonts"]["bold"], 16)
    draw.text((80, 80), f"— {topic}", fill=accent, font=top_f)

    # Título enorme tipo póster editorial
    title_fs = estimate_font_size(cfg["title"], W - 160, 220, cfg["fonts"]["title"], 68, 36)
    tf = load_font(cfg["fonts"]["title"], title_fs)
    lines_title = wrap_text(draw, cfg["title"], tf, W - 160)
    ty = 140
    for l in lines_title[:3]:
        draw.text((80, ty), l, fill=white, font=tf)
        ty += title_fs + 10

    # Línea divisoria elegante
    ty += 20
    draw.line([(80, ty), (240, ty)], fill=prim, width=4)
    ty += 40

    # Cuerpo editorial
    bf = load_font(cfg["fonts"]["body"], 24)
    lines_body = wrap_text(draw, cfg.get("body", cfg.get("tagline", "")), bf, W - 160)
    for l in lines_body[:7]:
        draw.text((80, ty), l, fill=(241, 245, 249, 240), font=bf)
        ty += 38

    # CTA sutil al pie
    cta_f = load_font(cfg["fonts"]["bold"], 20)
    draw.text((80, H - 120), f"→ {cfg.get('cta_text', '')}", fill=accent, font=cta_f)

    if cfg.get("hashtags"):
        ht_f = load_font(cfg["fonts"]["tagline"], 14)
        draw.text((80, H - 75), cfg["hashtags"], fill=hex_to_rgba(c["accent_light"], 160), font=ht_f)

# ─────────────────────────────────────────────────────────────
# LAYOUT 4: SPLIT (Visual Hero + Content Half)
# ─────────────────────────────────────────────────────────────
def render_split(draw: ImageDraw.Draw, img: Image.Image, cfg: dict, W: int, H: int):
    c = cfg["colors"]
    white = (255, 255, 255, 255)
    pd = hex_to_rgba(c["primary_dark"], 255)

    # Mitad superior para el diagrama o visual
    diag_path = cfg.get("diagram", "custom/diagram.svg")
    split_y = int(H * 0.44)

    if os.path.exists(diag_path) and render_diagram_card:
        render_diagram_card(img, diag_path, (60, 60, W - 60, split_y - 20), radius=24)
    else:
        draw.rounded_rectangle([60, 60, W - 60, split_y - 20], radius=24, fill=(255, 255, 255, 30), outline=(255, 255, 255, 80), width=1)
        tf = load_font(cfg["fonts"]["bold"], 26)
        draw.text((W // 2, split_y // 2), cfg.get("title", "Visual Hero"), fill=white, font=tf, anchor="mm")

    # Mitad inferior en tarjeta
    card_box = [60, split_y, W - 60, H - 60]
    draw.rounded_rectangle(card_box, radius=32, fill=hex_to_rgba(c["card_bg"], 240))

    # Título en tarjeta
    tf2 = load_font(cfg["fonts"]["title"], 32)
    draw.text((95, split_y + 35), cfg["title"], fill=pd, font=tf2)

    # Subtítulo / Tagline
    tag_f = load_font(cfg["fonts"]["tagline"], 18)
    draw.text((95, split_y + 80), cfg["tagline"], fill=hex_to_rgba(c["text_light"], 255), font=tag_f)

    # Bullets
    by = split_y + 125
    bf = load_font(cfg["fonts"]["body"], 18)
    for feat in cfg.get("features", [])[:3]:
        draw.text((95, by), f"• {feat.get('title')}: {feat.get('desc')}", fill=hex_to_rgba(c["text_body"], 255), font=bf)
        by += 32

    # Botón CTA
    draw.rounded_rectangle([95, H - 140, W - 95, H - 85], radius=18, fill=hex_to_rgba(c["primary"], 255))
    cta_f = load_font(cfg["fonts"]["bold"], 18)
    draw.text((W // 2, H - 113), cfg.get("cta_text", "Más información"), fill=white, font=cta_f, anchor="mm")

# ─────────────────────────────────────────────────────────────
# LAYOUT 5: QUOTE / INSIGHT
# ─────────────────────────────────────────────────────────────
def render_quote(draw: ImageDraw.Draw, img: Image.Image, cfg: dict, W: int, H: int):
    c = cfg["colors"]
    white = (255, 255, 255, 255)
    accent = hex_to_rgba(c["accent_light"], 255)

    # Comilla decorativa gigante
    q_font = load_font(cfg["fonts"]["title"], 180)
    draw.text((80, 60), "“", fill=hex_to_rgba(c["accent_light"], 120), font=q_font)

    # Cita / Texto central
    quote_text = cfg.get("body", cfg.get("title", ""))
    q_size = estimate_font_size(quote_text, W - 180, 400, cfg["fonts"]["title"], 48, 28)
    qf = load_font(cfg["fonts"]["title"], q_size)
    lines = wrap_text(draw, quote_text, qf, W - 180)

    qy = 260
    for l in lines[:7]:
        draw.text((90, qy), l, fill=white, font=qf)
        qy += q_size + 14

    # Autor o fuente
    qy += 40
    af = load_font(cfg["fonts"]["bold"], 24)
    draw.text((90, qy), f"— {cfg.get('tagline', '')}", fill=accent, font=af)

    # Footer
    cta_f = load_font(cfg["fonts"]["body"], 18)
    draw.text((90, H - 100), f"🔗 {cfg.get('cta_text', '')}", fill=white, font=cta_f)

    if cfg.get("hashtags"):
        ht_f = load_font(cfg["fonts"]["tagline"], 14)
        draw.text((90, H - 60), cfg["hashtags"], fill=hex_to_rgba(c["accent_light"], 180), font=ht_f)

# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL DE ORQUESTACIÓN
# ─────────────────────────────────────────────────────────────
def generate_post(cfg: dict = None, cli_args: list[str] = None):
    if cfg is None:
        cfg = load_config()

    # Procesar argumentos CLI si existen
    if cli_args:
        i = 0
        while i < len(cli_args):
            arg = cli_args[i]
            if arg == "--layout" and i + 1 < len(cli_args):
                cfg["layout"] = cli_args[i+1]
                i += 2
            elif arg == "--aspect" and i + 1 < len(cli_args):
                cfg["aspect"] = cli_args[i+1]
                i += 2
            elif arg == "--stock" and i + 1 < len(cli_args):
                cfg["stock"] = cli_args[i+1]
                i += 2
            elif arg == "--diagram" and i + 1 < len(cli_args):
                cfg["diagram"] = cli_args[i+1]
                cfg["layout"] = "diagram"
                i += 2
            else:
                i += 1

    # Validación Anti-IA Slop
    if lint_config:
        lint_res = lint_config(cfg)
        if not lint_res["clean"]:
            print(f"🛡️  [Anti-IA Slop] Puntuación de autenticidad: {lint_res['score']}/100 ({len(lint_res['issues'])} avisos)")
        else:
            print("🛡️  [Anti-IA Slop] Copy verificado: auténtico, directo y libre de clichés (100/100)")

    # Determinar dimensiones
    aspect = cfg.get("aspect", "1:1")
    W, H = ASPECT_RATIOS.get(aspect, (1080, 1080))
    if "width" in cfg and "height" in cfg:
        W, H = int(cfg["width"]), int(cfg["height"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CUSTOM_DIR, exist_ok=True)

    # ── Gestión de Logo de Marca y Extracción de Paleta ──
    logo_cfg = cfg.get("logo")
    logo_path = None
    logo_position = "top-right"
    logo_height = 55
    logo_badge = False

    if isinstance(logo_cfg, dict):
        logo_path = logo_cfg.get("path")
        logo_position = logo_cfg.get("position", "top-right")
        logo_height = logo_cfg.get("height", 55)
        logo_badge = logo_cfg.get("badge", False)
        if logo_cfg.get("extract_palette") and logo_path and os.path.exists(logo_path) and extract_brand_palette:
            print(f"🎨 Extrayendo paleta cromática del logo: {logo_path}")
            extracted = extract_brand_palette(logo_path)
            deep_merge(cfg["colors"], extracted)
    elif isinstance(logo_cfg, str):
        logo_path = logo_cfg

    # Si se pide auto-extracción vía bandera o config
    if cfg.get("extract_palette") and logo_path and os.path.exists(logo_path) and extract_brand_palette:
        extracted = extract_brand_palette(logo_path)
        deep_merge(cfg["colors"], extracted)

    # ── Construcción del fondo ──
    background_path = cfg.get("background")
    stock_query = cfg.get("stock")

    # Si se especificó stock o se pasó búsqueda de banco libre
    if stock_query and fetch_stock_background:
        try:
            overlay_mode = "dark"
            blur_val = 0
            q = stock_query
            if isinstance(stock_query, dict):
                q = stock_query.get("query", "")
                overlay_mode = stock_query.get("overlay", "dark")
                blur_val = stock_query.get("blur", 0)

            print(f"🖼️  Obteniendo fondo libre de Openverse/Wikimedia...")
            background_path = fetch_stock_background(q, (W, H), overlay=overlay_mode, blur=blur_val)
        except Exception as e:
            print(f"⚠️  No se pudo obtener imagen de stock ({e}). Usando gradiente.")
            background_path = None

    if background_path and os.path.exists(background_path):
        bg = Image.open(background_path).convert("RGBA")
        if bg.size != (W, H):
            bg = bg.resize((W, H), Image.LANCZOS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.paste(bg, (0, 0), bg)
    else:
        # Gradiente moderno de alta definición
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_g = ImageDraw.Draw(img)
        draw_gradient(draw_g, W, H, cfg["colors"]["gradient_top"], cfg["colors"]["gradient_bottom"])

        # Micro-textura moderna (rejilla de puntos sutiles anti-slop)
        grid_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_grid = ImageDraw.Draw(grid_overlay)
        step = 48
        for gx in range(40, W - 40, step):
            for gy in range(40, H - 40, step):
                draw_grid.ellipse([gx, gy, gx + 2, gy + 2], fill=(255, 255, 255, 12))
        img.alpha_composite(grid_overlay)

    draw = ImageDraw.Draw(img)

    # ── Renderizado del Layout ──
    layout = cfg.get("layout", "card")
    if layout == "diagram":
        render_diagram_layout(draw, img, cfg, W, H)
    elif layout == "minimal":
        render_minimal(draw, img, cfg, W, H)
    elif layout == "split":
        render_split(draw, img, cfg, W, H)
    elif layout == "quote":
        render_quote(draw, img, cfg, W, H)
    else: # default 'card'
        render_card(draw, img, cfg, W, H)

    # ── Superposición de Logo de Marca ──
    if logo_path and os.path.exists(logo_path) and render_brand_logo:
        render_brand_logo(
            img,
            logo_path,
            position=logo_position,
            height=logo_height,
            badge=logo_badge
        )

    # ── Guardado Final ──
    output_path = os.path.join(ROOT, cfg.get("output", "output/post.png"))
    final = img.convert("RGB")
    final.save(output_path, "PNG", quality=95)
    print(f"✅ Post generado con éxito: {output_path}")
    print(f"   Layout: {layout} | Ratio: {aspect} ({W}×{H}px)")
    return output_path

def main():
    config_file = None
    args = sys.argv[1:]

    if "--config" in args:
        idx = args.index("--config")
        if idx + 1 < len(args):
            config_file = args[idx + 1]

    cfg = load_config(config_file)
    generate_post(cfg, cli_args=args)

if __name__ == "__main__":
    main()
