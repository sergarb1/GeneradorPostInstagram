#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

AI_MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) AI_MODE="$2"; shift 2 ;;
    --ai=*) AI_MODE="${1#*=}"; shift ;;
    *) echo "Uso: $0 [--ai opencode|codex|gemini|claude]"; exit 1 ;;
  esac
done

command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3"; exit 1; }

CONTEXT_FILE="custom/context.md"

if [ -n "$AI_MODE" ]; then
  if [ ! -f "$CONTEXT_FILE" ]; then
    echo "📝 Describe tu proyecto (texto libre, luego Ctrl+D):"
    mkdir -p custom
    cat > "$CONTEXT_FILE"
    echo "✓ Guardado en $CONTEXT_FILE"
  fi

  CONTEXT=$(cat "$CONTEXT_FILE")
  echo "🤖 Generando config con $AI_MODE..."

  GENERATED=""
  case "$AI_MODE" in
    opencode)
      if command -v opencode >/dev/null 2>&1; then
        GENERATED=$(echo "$CONTEXT" | opencode --prompt "
          A partir de este contexto de proyecto, genera un archivo YAML 'config.yaml'
          para un post de Instagram promocional.
          El YAML debe tener: title, tagline, body (con saltos de línea \n),
          features (4 items con icon/title/desc), cta_text, hashtags.
          Responde SÓLO con el YAML, sin explicaciones.")
      else
        echo "⚠️  opencode no instalado. Usando modo interactivo."
      fi
      ;;
    gemini)
      if command -v gemini >/dev/null 2>&1; then
        GENERATED=$(echo "$CONTEXT" | gemini --prompt "
          Genera un archivo YAML 'config.yaml' para un post de Instagram.
          Incluye: title, tagline, body, features (4 items), cta_text, hashtags.
          Responde solo con el YAML.")
      else
        echo "⚠️  gemini no instalado. Usando modo interactivo."
      fi
      ;;
    codex)
      if command -v codex >/dev/null 2>&1; then
        GENERATED=$(echo "$CONTEXT" | codex --prompt "
          Generate a YAML config for an Instagram post.
          Include: title, tagline, body, features (4 items), cta_text, hashtags.
          Output only YAML.")
      else
        echo "⚠️  codex no instalado. Usando modo interactivo."
      fi
      ;;
    claude)
      if command -v claude >/dev/null 2>&1; then
        GENERATED=$(echo "$CONTEXT" | claude --prompt "
          Genera un archivo YAML 'config.yaml' para un post de Instagram promocional.
          Incluye: title, tagline, body, features (4 items con icon/title/desc), cta_text, hashtags.
          Responde solo con el YAML, sin explicaciones.")
      else
        echo "⚠️  claude no instalado. Usando modo interactivo."
      fi
      ;;
    *)
      echo "⚠️  IA '$AI_MODE' no reconocida. Opciones: opencode, codex, gemini, claude"
      ;;
  esac

  if [ -n "$GENERATED" ]; then
    mkdir -p custom
    echo "$GENERATED" > custom/config.generated.yaml
    echo "✓ Config generada por IA guardada en custom/config.generated.yaml"
  fi
fi

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
" 2>/dev/null || echo "⚠️  No se pudieron descargar fuentes."
fi

echo "📦 Verificando dependencias..."
pip3 install -q --break-system-packages pillow pyyaml requests 2>/dev/null || pip install -q --break-system-packages pillow pyyaml requests 2>/dev/null || pip install -q pillow pyyaml requests

echo "🖼  Generando post..."

if [ -n "$AI_MODE" ] && [ -f "custom/config.generated.yaml" ]; then
  python3 post.py
else
  python3 post.py --interactive
fi
