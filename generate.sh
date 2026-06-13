#!/usr/bin/env bash
# Generador de posts Instagram — Linux/Mac
# Soporta: opencode, codex, gemini, claude para generación automática de contenido
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── parse args ──────────────────────────────────────────────
AI_MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) AI_MODE="$2"; shift 2 ;;
    --ai=*) AI_MODE="${1#*=}"; shift ;;
    *) echo "Uso: $0 [--ai opencode|codex|gemini|claude]"; exit 1 ;;
  esac
done

# ── check deps ──────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3"; exit 1; }

# ── IA: generar config desde context.md ────────────────────
CONTEXT_FILE="custom/context.md"
CONFIG_FILE="config.yaml"

if [ -n "$AI_MODE" ] && [ -f "$CONTEXT_FILE" ]; then
  CONTEXT=$(cat "$CONTEXT_FILE")
  echo "🤖 Generando config con $AI_MODE..."

  case "$AI_MODE" in
    opencode)
      if command -v opencode >/dev/null 2>&1; then
        echo "$CONTEXT" | opencode --prompt "
          A partir de este contexto de proyecto, genera un archivo YAML 'config.yaml' 
          para un post de Instagram promocional.
          El YAML debe tener: title, tagline, body (con saltos de línea \n), 
          features (4 items con icon/title/desc), cta_text, hashtags.
          Responde SÓLO con el YAML, sin explicaciones."
      else
        echo "⚠️  opencode no instalado. Usando config por defecto."
      fi
      ;;
    gemini)
      if command -v gemini >/dev/null 2>&1; then
        echo "$CONTEXT" | gemini --prompt "
          Genera un archivo YAML 'config.yaml' para un post de Instagram.
          Incluye: title, tagline, body, features (4 items), cta_text, hashtags.
          Responde solo con el YAML."
      else
        echo "⚠️  gemini no instalado. Usando config por defecto."
      fi
      ;;
    codex)
      if command -v codex >/dev/null 2>&1; then
        echo "$CONTEXT" | codex --prompt "
          Generate a YAML config for an Instagram post.
          Include: title, tagline, body, features (4 items), cta_text, hashtags.
          Output only YAML."
      else
        echo "⚠️  codex no instalado. Usando config por defecto."
      fi
      ;;
    claude)
      if command -v claude >/dev/null 2>&1; then
        echo "$CONTEXT" | claude --prompt "
          Genera un archivo YAML 'config.yaml' para un post de Instagram promocional.
          Incluye: title, tagline, body, features (4 items con icon/title/desc), cta_text, hashtags.
          Responde solo con el YAML, sin explicaciones."
      else
        echo "⚠️  claude no instalado. Usando config por defecto."
      fi
      ;;
    *)
      echo "⚠️  IA '$AI_MODE' no reconocida. Opciones: opencode, codex, gemini, claude"
      ;;
  esac
elif [ -n "$AI_MODE" ]; then
  echo "⚠️  No hay custom/context.md. Crea uno o usa la configuración por defecto."
fi

# ── descargar fuentes ──────────────────────────────────────
if [ ! -d "fonts" ] || [ -z "$(ls -A fonts/ 2>/dev/null)" ]; then
  echo "📥 Descargando fuentes..."
  mkdir -p fonts
  python3 -c "
import requests, os
fonts = {
  'Outfit-Bold.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4deyC4E.ttf',
  'Outfit-Regular.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4TC1C4E.ttf',
}
for name, url in fonts.items():
  r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
  with open(f'fonts/{name}', 'wb') as f:
    f.write(r.content)
  print(f'  {name} descargado')
" 2>/dev/null || echo "⚠️  No se pudieron descargar fuentes. Usando fuente por defecto."
fi

# ── instalar deps ──────────────────────────────────────────
echo "📦 Verificando dependencias..."
pip3 install -q --break-system-packages pillow pyyaml requests 2>/dev/null || pip install -q --break-system-packages pillow pyyaml requests

# ── generar post ───────────────────────────────────────────
echo "🖼  Generando post..."
python3 post.py
