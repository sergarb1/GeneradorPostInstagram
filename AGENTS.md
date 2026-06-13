# GeneradorPostInstagram — AGENTS.md

## Project
Genera imágenes promocionales 1080×1080 para Instagram desde YAML config. Funciona sin IA o con apoyo de opencode, Gemini CLI, Codex o Claude.

## Stack
- Python 3 + Pillow (imagen)
- pyyaml (config)
- requests (descarga fuentes)
- Sin servidor, sin build, 100% local

## GitHub
- Repo: `github.com/sergarb1/GeneradorPostInstagram`
- Pages: `https://sergarb1.github.io/GeneradorPostInstagram/`

## File Structure
```
GeneradorPostInstagram/
├── post.py              # Core: lee YAML, dibuja con Pillow, guarda PNG
├── config.yaml          # Config principal (título, features, colores, etc.)
├── requirements.txt     # Dependencias Python
├── generate.sh          # Script Linux/Mac
├── generate.bat         # Script Windows
├── index.html           # Landing page del proyecto
├── templates/
│   └── default.json     # Plantilla visual (layout card)
├── custom/              # GITIGNORED — datos del usuario
│   ├── context.md       # Contexto del proyecto para IA
│   ├── logo.png         # Logo personalizado
│   └── config.local.yaml# Sobreescribe config.yaml
├── output/              # GITIGNORED — posts generados
├── fonts/               # GITIGNORED — fuentes descargadas
├── AGENTS.md
├── README.md
└── LICENSE (AGPL v3)
```

## Key Functions (post.py)
- `load_config()` → YAML → dict, merge con config.local.yaml si existe
- `deep_merge(base, override)` → merge recursivo de dicts
- `draw_gradient(draw, w, h, color_top, color_bottom)` → gradiente vertical
- `render_card(draw, cfg)` → layout card con header, body, features, CTA
- `main()` → orquesta: background, decoraciones, render, logo overlay, guardado

## Config YAML
```yaml
title: "Nombre del proyecto"         # Título grande
tagline: "Frase corta"               # Subtítulo
body: "Texto principal\ncon saltos"  # Cuerpo del post
features:                            # Lista de features (hasta 4)
  - icon: "🎯" title: "Feature" desc: "Descripción"
cta_text: "url.com"                  # Texto del botón CTA
hashtags: "#hash #tags"              # Hashtags al pie
colors:
  primary: "#hex"                    # Color principal
  gradient_top: "#hex"               # Superior del gradiente
  gradient_bottom: "#hex"            # Inferior del gradiente
fonts:
  title: "Font.ttf"                  # Fuente (se descarga automáticamente)
layout: "card"                       # Solo card por ahora
logo: null                           # Ruta a logo en custom/
output: "output/post.png"            # Archivo de salida
```

## AI Mode (generate.sh)
- `--ai opencode` → llama a opencode con el context.md
- `--ai gemini` → llama a gemini CLI
- `--ai codex` → llama a codex CLI
- `--ai claude` → llama a claude CLI
- Si no hay herramienta o no hay context.md → usa config por defecto

## Tips
- custom/config.local.yaml hace merge profundo: sobreescribe solo las claves que pongas
- Las fuentes se descargan automáticamente al ejecutar generate.sh (Outfit Regular + Bold)
- Para probar rápido: `python3 post.py` genera output/post.png
- Los colores en YAML pueden ser hex (#rrggbb) o hex con alpha (#rrggbbaa para card_bg)
- El index.html es una landing page informativa; no necesita build
