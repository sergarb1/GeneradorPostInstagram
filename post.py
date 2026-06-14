#!/usr/bin/env python3
import os, sys, yaml, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")
CUSTOM_DIR = os.path.join(ROOT, "custom")
OUTPUT_DIR = os.path.join(ROOT, "output")

PX = 1080
CARD_X = 60
CARD_W = PX - 120
CARD_R = 40
HASHTAG_Y = 1010

def load_font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        fonts = [f for f in os.listdir(FONT_DIR) if f.endswith(".ttf")] if os.path.isdir(FONT_DIR) else []
        if fonts:
            return ImageFont.truetype(os.path.join(FONT_DIR, fonts[0]), size)
        return ImageFont.load_default()

def hex_to_rgba(h, alpha=255):
    h = h.lstrip("#")
    parts = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    if len(parts) == 4:
        return tuple(parts)
    return tuple(parts) + (alpha,)

def rounded_rect(draw, xy, radius, fill, outline=None, width=0):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_gradient(draw, w, h, color_top, color_bottom):
    top = hex_to_rgba(color_top, 255)
    bot = hex_to_rgba(color_bottom, 255)
    for y in range(h):
        r = int(top[0] * (1 - y/h) + bot[0] * (y/h))
        g = int(top[1] * (1 - y/h) + bot[1] * (y/h))
        b = int(top[2] * (1 - y/h) + bot[2] * (y/h))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

def estimate_font_size(text, max_w, max_h, font_name, start_size=50, min_size=12):
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

def wrap_text(draw, text, font, max_w):
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

def deep_merge(base, override):
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v

def load_config():
    with open(os.path.join(ROOT, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    for name in ("config.local.yaml", "config.generated.yaml"):
        path = os.path.join(CUSTOM_DIR, name)
        if os.path.exists(path):
            with open(path) as f:
                data = yaml.safe_load(f)
                if data:
                    deep_merge(cfg, data)
    return cfg

def prompt_field(label, default, allow_empty=False):
    if default and str(default) != "None":
        raw = input(f"{label} [{default}]: ").strip()
    else:
        raw = input(f"{label}: ").strip()
    if not raw:
        return "" if allow_empty else (default or "")
    return raw

def prompt_features(defaults):
    want = input("📋 ¿Incluir features? [s/N]: ").strip().lower()
    if want != "s":
        return defaults or []
    features = []
    for i in range(4):
        print(f"\n  Feature {i+1}:")
        di = defaults[i] if i < len(defaults) else {}
        icon = input(f"    Icono [{di.get('icon', '🎯')}]: ").strip()
        if not icon:
            if i < len(defaults):
                icon = di.get("icon", "🎯")
            else:
                break
        title = prompt_field("    Título", di.get("title", ""))
        desc = prompt_field("    Descripción", di.get("desc", ""))
        features.append({"icon": icon, "title": title, "desc": desc})
    return features

def interactive():
    os.makedirs(CUSTOM_DIR, exist_ok=True)
    gen_path = os.path.join(CUSTOM_DIR, "config.generated.yaml")
    defaults = {}
    if os.path.exists(gen_path):
        with open(gen_path) as f:
            defaults = yaml.safe_load(f) or {}
    print("\n🎨 Generador de posts Instagram — modo interactivo")
    print("   (Enter para mantener valor anterior)\n")
    cfg = {}
    cfg["title"] = prompt_field("🎯 Título del post", defaults.get("title", ""))
    cfg["tagline"] = prompt_field("📝 Tagline", defaults.get("tagline", ""))
    cfg["cta_text"] = prompt_field("🔗 Llamada a la acción", defaults.get("cta_text", ""))
    cfg["hashtags"] = prompt_field("🏷️ Hashtags", defaults.get("hashtags", ""), allow_empty=True)
    cfg["features"] = prompt_features(defaults.get("features", []))
    bg = prompt_field("🖼️  Imagen de fondo (ruta o vacío para degradado)", defaults.get("background", ""), allow_empty=True)
    if bg:
        cfg["background"] = bg
    with open(gen_path, "w") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    print(f"\n💾 Guardado en {gen_path}\n")

def render_card(draw, cfg):
    W = PX
    c = cfg["colors"]

    # ── header ──
    logo_font = load_font(cfg["fonts"]["title"], 48)
    tag_font = load_font(cfg["fonts"]["tagline"], 22)
    white = (255, 255, 255)
    accent = hex_to_rgba(c["accent_light"], 255)
    draw.text((75, 60), "✨", fill=white, font=logo_font)
    title_fs = estimate_font_size(cfg["title"], 700, 60, cfg["fonts"]["title"], 48, 24)
    tf = load_font(cfg["fonts"]["title"], title_fs)
    draw.text((170, 67), cfg["title"], fill=white, font=tf)
    draw.text((75, 130), cfg["tagline"], fill=accent, font=tag_font)

    # ── card background ──
    card_y = 210
    card_h = 540
    card_bg_hex = c.get("card_bg", "#ffffffeb")
    card_color = hex_to_rgba(card_bg_hex, 235) if len(card_bg_hex) == 9 else (255, 255, 255, 235)
    rounded_rect(draw, (CARD_X, card_y, CARD_X + CARD_W, card_y + card_h), CARD_R, card_color)

    # ── body ──
    pd = hex_to_rgba(c["primary_dark"], 255)
    body_font = load_font(cfg["fonts"]["bold"], 28)
    draw.text((100, card_y + 30), "🚀  ¿Qué es?", fill=pd, font=body_font)
    rounded_rect(draw, (100, card_y + 75, 450, card_y + 79), 3, hex_to_rgba(c["primary"], 255))
    bf = load_font(cfg["fonts"]["body"], 20)
    max_body_w = CARD_W - 80
    lines = wrap_text(draw, cfg["body"], bf, max_body_w)
    body_color = hex_to_rgba(c["text_body"], 255)
    by = card_y + 100
    for line in lines[:8]:
        draw.text((100, by), line, fill=body_color, font=bf)
        by += 28

    # ── features ──
    feat_y = card_y + 290
    sf = load_font(cfg["fonts"]["bold"], 20)
    df = load_font(cfg["fonts"]["body"], 16)
    for feat in cfg["features"]:
        draw.ellipse([100, feat_y, 132, feat_y + 32], fill=accent)
        draw.text((108, feat_y + 3), feat["icon"], fill=pd, font=df)
        draw.text((150, feat_y), feat["title"], fill=pd, font=sf)
        draw.text((150, feat_y + 28), feat["desc"], fill=hex_to_rgba(c["text_light"], 255), font=df)
        feat_y += 55

    # ── CTA ──
    cta_y = card_y + card_h + 30
    rounded_rect(draw, (180, cta_y, W - 180, cta_y + 65), 35, white)
    cta_font = load_font(cfg["fonts"]["bold"], 22)
    cta_text = f"🌐  {cfg['cta_text']}"
    cta_fs = estimate_font_size(cta_text, W - 420, 40, cfg["fonts"]["bold"], 22, 12)
    cf = load_font(cfg["fonts"]["bold"], cta_fs)
    draw.text((W // 2, cta_y + 15), cta_text, fill=pd, font=cf, anchor="mt")
    draw.text((810, cta_y + 13), "→", fill=hex_to_rgba(c["primary"], 255), font=cf)

    # ── hashtags ──
    ht_font = load_font(cfg["fonts"]["tagline"], 16)
    draw.text((W // 2, HASHTAG_Y), cfg["hashtags"], fill=accent, font=ht_font, anchor="mt")

def main():
    if "-i" in sys.argv or "--interactive" in sys.argv:
        interactive()

    cfg = load_config()
    W = H = PX
    os.makedirs(FONT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    background_path = cfg.get("background")

    # ── create base image ──
    if background_path and os.path.exists(background_path):
        bg = Image.open(background_path).convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.paste(bg, (0, 0), bg)
    else:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_gradient(draw, W, H, cfg["colors"]["gradient_top"], cfg["colors"]["gradient_bottom"])

    draw = ImageDraw.Draw(img)

    # ── decorative circles (only on gradient backgrounds) ──
    if not background_path or not os.path.exists(background_path):
        draw.ellipse([-150, -150, 300, 300], fill=(255, 255, 255, 14))
        draw.ellipse([W - 230, -100, W + 120, 250], fill=(255, 255, 255, 10))
        draw.ellipse([700, 700, 1300, 1300], fill=(255, 255, 255, 8))
        draw.ellipse([-200, 600, 200, 1000], fill=(255, 255, 255, 8))
        draw.ellipse([400, 350, 900, 850], fill=(255, 255, 255, 5))
        rounded_rect(draw, (40, 25, W - 40, 33), 4, (255, 255, 255, 60))

    # ── layout ──
    layout = cfg.get("layout", "card")
    if layout == "card":
        render_card(draw, cfg)

    # ── logo overlay ──
    logo_path = cfg.get("logo")
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((80, 80))
            img.paste(logo, (W - 120, 60), logo)
        except Exception:
            pass

    # ── save ──
    out = os.path.join(ROOT, cfg.get("output", "output/post.png"))
    final = img.convert("RGB")
    final.save(out, "PNG")
    print(f"✅ Post generado: {out}")
    print(f"   Tamaño: {final.size[0]}×{final.size[1]}")

if __name__ == "__main__":
    main()
