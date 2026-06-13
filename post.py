#!/usr/bin/env python3
import os, sys, yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")
CUSTOM_DIR = os.path.join(ROOT, "custom")
OUTPUT_DIR = os.path.join(ROOT, "output")

def load_font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        fonts = [f for f in os.listdir(FONT_DIR) if f.endswith(".ttf")] if os.path.isdir(FONT_DIR) else []
        if fonts:
            return ImageFont.truetype(os.path.join(FONT_DIR, fonts[0]), size)
        return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rounded_rect(draw, xy, radius, fill, outline=None, width=0):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_gradient(draw, w, h, color_top, color_bottom):
    top = hex_to_rgb(color_top)
    bot = hex_to_rgb(color_bottom)
    for y in range(h):
        r = int(top[0] * (1 - y/h) + bot[0] * (y/h))
        g = int(top[1] * (1 - y/h) + bot[1] * (y/h))
        b = int(top[2] * (1 - y/h) + bot[2] * (y/h))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

def deep_merge(base, override):
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v

def load_config():
    with open(os.path.join(ROOT, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    local_cfg = os.path.join(CUSTOM_DIR, "config.local.yaml")
    if os.path.exists(local_cfg):
        with open(local_cfg) as f:
            local = yaml.safe_load(f)
            if local:
                deep_merge(cfg, local)
    gen_cfg = os.path.join(CUSTOM_DIR, "config.generated.yaml")
    if os.path.exists(gen_cfg):
        with open(gen_cfg) as f:
            gen = yaml.safe_load(f)
            if gen:
                deep_merge(cfg, gen)
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
        default_icon = defaults[i]["icon"] if i < len(defaults) and defaults[i].get("icon") else "🎯"
        icon = input(f"    Icono [{default_icon}]: ").strip()
        if not icon:
            if i < len(defaults):
                icon = defaults[i].get("icon", "🎯")
            else:
                break
        title = prompt_field("    Título", defaults[i]["title"] if i < len(defaults) else "")
        desc = prompt_field("    Descripción", defaults[i]["desc"] if i < len(defaults) else "")
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

    with open(gen_path, "w") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    print(f"\n💾 Guardado en {gen_path}\n")

def render_card(draw, cfg):
    W = cfg.get("width", 1080)
    c = cfg["colors"]
    p = hex_to_rgb(c["primary"])
    pd = hex_to_rgb(c["primary_dark"])
    font_logo = load_font(cfg["fonts"]["title"], 52)
    font_tag = load_font(cfg["fonts"]["tagline"], 24)
    draw.text((80, 65), "✨", fill=(255,255,255), font=font_logo)
    draw.text((175, 72), cfg["title"], fill=(255,255,255), font=font_logo)
    draw.text((80, 135), cfg["tagline"], fill=hex_to_rgb(c["accent_light"]), font=font_tag)
    card_y = 210
    card_h = 500
    card_bg = cfg["colors"].get("card_bg", "#ffffffeb")
    card_color = tuple(int(card_bg[i:i+2], 16) for i in (1, 3, 5, 7)) if len(card_bg) == 9 else (255, 255, 255, 235)
    rounded_rect(draw, (60, card_y, W - 60, card_y + card_h), 40, card_color)
    rounded_rect(draw, (100, card_y + 35, 500, card_y + 40), 3, p)
    font_title = load_font(cfg["fonts"]["bold"], 34)
    draw.text((100, card_y + 65), "🚀  ¿Qué es?", fill=pd, font=font_title)
    font_body = load_font(cfg["fonts"]["body"], 20)
    body_color = hex_to_rgb(c["text_body"])
    lines = cfg["body"].split("\n")
    y = card_y + 135
    for line in lines:
        draw.text((100, y), line, fill=body_color, font=font_body)
        y += 32
    font_sub = load_font(cfg["fonts"]["bold"], 22)
    font_small = load_font(cfg["fonts"]["body"], 17)
    accent = hex_to_rgb(c["accent_light"])
    item_y = card_y + 260
    for feat in cfg["features"]:
        draw.ellipse([100, item_y - 5, 140, item_y + 35], fill=accent)
        draw.text((109, item_y + 2), feat["icon"], fill=pd, font=load_font(cfg["fonts"]["body"], 22))
        draw.text((160, item_y - 2), feat["title"], fill=pd, font=font_sub)
        draw.text((160, item_y + 32), feat["desc"], fill=hex_to_rgb(c["text_light"]), font=font_small)
        item_y += 80
    cta_y = card_y + card_h + 35
    rounded_rect(draw, (150, cta_y, W - 150, cta_y + 70), 40, (255, 255, 255))
    font_cta = load_font(cfg["fonts"]["bold"], 22)
    draw.text((W // 2, cta_y + 20), f"🌐  {cfg['cta_text']}", fill=pd, font=font_cta, anchor="mt")
    draw.text((780, cta_y + 18), "→", fill=p, font=font_cta)
    font_bot = load_font(cfg["fonts"]["tagline"], 16)
    draw.text((W // 2, 1020), cfg["hashtags"], fill=hex_to_rgb(c["accent_light"]), font=font_bot, anchor="mt")

def main():
    if "-i" in sys.argv or "--interactive" in sys.argv:
        interactive()
    cfg = load_config()
    W = cfg.get("width", 1080)
    H = cfg.get("height", 1080)
    os.makedirs(FONT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, cfg["colors"]["gradient_top"], cfg["colors"]["gradient_bottom"])
    draw.ellipse([-150, -150, 300, 300], fill=(255, 255, 255, 12))
    draw.ellipse([W - 230, -100, W + 120, 250], fill=(255, 255, 255, 8))
    draw.ellipse([700, 700, 1300, 1300], fill=(255, 255, 255, 6))
    draw.ellipse([-200, 600, 200, 1000], fill=(255, 255, 255, 8))
    draw.ellipse([400, 350, 900, 850], fill=(255, 255, 255, 4))
    rounded_rect(draw, (40, 30, W - 40, 38), 4, (255, 255, 255, 60))
    layout = cfg.get("layout", "card")
    if layout == "card":
        render_card(draw, cfg)
    logo_path = cfg.get("logo")
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((80, 80))
            img.paste(logo, (W - 120, 60), logo)
        except Exception:
            pass
    out = os.path.join(ROOT, cfg.get("output", "output/post.png"))
    img.save(out, "PNG")
    print(f"✅ Post generado: {out}")
    print(f"   Tamaño: {img.size[0]}×{img.size[1]}")

if __name__ == "__main__":
    main()
