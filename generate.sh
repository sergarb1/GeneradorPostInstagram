#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE_FILE="custom/.mode"

command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3"; exit 1; }

# ── parse args ──────────────────────────────────────────────
OVERRIDE_MODE=""
RESET_MODE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) OVERRIDE_MODE="$2"; shift 2 ;;
    --ai=*) OVERRIDE_MODE="${1#*=}"; shift ;;
    --reset-mode) RESET_MODE=true; shift ;;
    *) echo "Uso: $0 [--ai opencode|codex|gemini|claude] [--reset-mode]"; exit 1 ;;
  esac
done

# ── elegir modo ─────────────────────────────────────────────
choose_mode() {
  echo ""
  echo "🎨 ¿Cómo quieres crear tu post de Instagram?"
  echo ""
  echo "  1) Manual — te guío paso a paso con preguntas"
  echo "  2) opencode — IA local que trabaja con tu código"
  echo "  3) Gemini CLI — la IA de Google"
  echo "  4) Codex CLI — la IA de OpenAI para terminal"
  echo "  5) Claude CLI — la IA de Anthropic"
  echo ""
  read -p "Elige (1-5) [1]: " choice
  choice="${choice:-1}"
  case "$choice" in
    1) echo "manual" ;;
    2) echo "opencode" ;;
    3) echo "gemini" ;;
    4) echo "codex" ;;
    5) echo "claude" ;;
    *) echo "manual" ;;
  esac
}

MODE="$OVERRIDE_MODE"
if [ -z "$MODE" ]; then
  if [ "$RESET_MODE" = true ] || [ ! -f "$MODE_FILE" ]; then
    mkdir -p custom
    MODE=$(choose_mode)
    echo "$MODE" > "$MODE_FILE"
    echo "✓ Modo guardado (usa --reset-mode para cambiarlo)"
  else
    MODE=$(cat "$MODE_FILE")
  fi
fi

echo "📋 Modo: $MODE"

# ── dependencias + fuentes ──────────────────────────────────
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

# ── modo manual ────────────────────────────────────────────
if [ "$MODE" = "manual" ]; then
  python3 post.py --interactive
  exit 0
fi

# ── modo IA ─────────────────────────────────────────────────
CONTEXT_FILE="custom/context.md"

# Si no hay contexto, pedirlo
if [ ! -f "$CONTEXT_FILE" ]; then
  echo ""
  echo "📝 Cuéntame sobre tu proyecto:"
  echo "   (Escribe una descripción libre. Ctrl+D para terminar.)"
  echo ""
  mkdir -p custom
  cat > "$CONTEXT_FILE"
  echo "✓ Guardado en $CONTEXT_FILE"
fi

CONTEXT=$(cat "$CONTEXT_FILE")
echo "🤖 Generando configuración con $MODE..."

# ── prompt base para todas las IAs ─────────────────────────
BASE_PROMPT="Eres un experto en marketing educativo y redes sociales. Tu tarea es crear la configuración YAML para un post promocional de Instagram a partir de la descripción de un proyecto.

La configuración debe incluir estas claves YAML:
  - title: título llamativo del post (máximo 40 caracteres)
  - tagline: frase corta de apoyo (máximo 60 caracteres)
  - body: texto principal del post, puede usar \n para saltos de línea (máximo 200 caracteres)
  - features: lista de 4 elementos, cada uno con icon (emoji), title (corto) y desc (una línea)
  - cta_text: texto del botón de llamada a la acción (una URL o texto corto)
  - hashtags: cadena con hashtags separados por espacios

Reglas:
- Tono cercano, inspirador, profesional
- Los features deben destacar beneficios reales
- El título debe captar atención
- Responde ÚNICAMENTE con el YAML, sin explicaciones ni código alrededor

Contexto del proyecto:
---

$CONTEXT

---

YAML:"

# ── ejecutar según herramienta ──────────────────────────────
GENERATED=""
case "$MODE" in
  opencode)
    if command -v opencode >/dev/null 2>&1; then
      GENERATED=$(opencode --prompt "$BASE_PROMPT" 2>/dev/null)
    else
      echo "⚠️  opencode no está instalado."
      echo "   Instálalo con: npm install -g @opencode/cli"
      echo "   Mientras tanto, entro en modo manual."
    fi
    ;;
  gemini)
    if command -v gemini >/dev/null 2>&1; then
      GENERATED=$(gemini --prompt "$BASE_PROMPT" 2>/dev/null)
    else
      echo "⚠️  Gemini CLI no está instalado."
      echo "   Instálalo con: pip install google-generativeai"
      echo "   Mientras tanto, entro en modo manual."
    fi
    ;;
  codex)
    if command -v codex >/dev/null 2>&1; then
      GENERATED=$(codex --prompt "$BASE_PROMPT" 2>/dev/null)
    else
      echo "⚠️  Codex CLI no está instalado."
      echo "   Instálalo con: npm install -g @openai/codex"
      echo "   Mientras tanto, entro en modo manual."
    fi
    ;;
  claude)
    if command -v claude >/dev/null 2>&1; then
      GENERATED=$(claude --prompt "$BASE_PROMPT" 2>/dev/null)
    else
      echo "⚠️  Claude CLI no está instalado."
      echo "   Instálalo con: npm install -g @anthropic-ai/claude"
      echo "   Mientras tanto, entro en modo manual."
    fi
    ;;
esac

if [ -n "$GENERATED" ]; then
  mkdir -p custom
  echo "$GENERATED" > custom/config.generated.yaml
  echo "✓ Configuración generada por $MODE guardada en custom/config.generated.yaml"
  python3 post.py
else
  echo "ℹ️  No se pudo generar con IA. Usando modo manual."
  python3 post.py --interactive
fi
