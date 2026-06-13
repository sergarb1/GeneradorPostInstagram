#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE_FILE="custom/.mode"

command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3" >&2; exit 1; }

OVERRIDE_MODE=""
RESET_MODE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) OVERRIDE_MODE="$2"; shift 2 ;;
    --ai=*) OVERRIDE_MODE="${1#*=}"; shift ;;
    --reset-mode) RESET_MODE=true; shift ;;
    *) echo "Uso: $0 [--ai opencode|codex|gemini|claude] [--reset-mode]" >&2; exit 1 ;;
  esac
done

choose_mode() {
  echo "" >&2
  echo "🎨 ¿Cómo quieres crear tu post de Instagram?" >&2
  echo "" >&2
  echo "  1) Manual — te guío paso a paso con preguntas" >&2
  echo "  2) opencode — IA local que trabaja con tu código" >&2
  echo "  3) Gemini CLI — la IA de Google" >&2
  echo "  4) Codex CLI — la IA de OpenAI para terminal" >&2
  echo "  5) Claude CLI — la IA de Anthropic" >&2
  echo "" >&2
  read -p $'\e[1mElige (1-5) [1]:\e[0m ' choice
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
    echo "✓ Modo guardado (usa --reset-mode para cambiarlo)" >&2
  else
    MODE=$(cat "$MODE_FILE")
  fi
fi

echo "📋 Modo: $MODE" >&2

if [ ! -d "fonts" ] || [ -z "$(ls -A fonts/ 2>/dev/null)" ]; then
  echo "📥 Descargando fuentes..." >&2
  mkdir -p fonts
  python3 -c "
import requests, os
fonts = {
  'Outfit-Bold.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4deyC4E.ttf',
  'Outfit-Regular.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4TC1C4E.ttf',
}
for name, url in fonts.items():
  r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
  with open('fonts/' + name, 'wb') as f:
    f.write(r.content)
  print(f'  {name} descargado')
" 2>/dev/null || echo "⚠️  No se pudieron descargar fuentes." >&2
fi

echo "📦 Verificando dependencias..." >&2
pip3 install -q --break-system-packages pillow pyyaml requests 2>/dev/null || pip install -q --break-system-packages pillow pyyaml requests 2>/dev/null || pip install -q pillow pyyaml requests

if [ "$MODE" = "manual" ]; then
  python3 post.py --interactive
  exit 0
fi

CONTEXT_FILE="custom/context.md"

if [ ! -f "$CONTEXT_FILE" ]; then
  echo "" >&2
  echo "📝 Cuéntame sobre tu proyecto:" >&2
  echo "   (Escribe una descripción libre. Ctrl+D para terminar.)" >&2
  echo "" >&2
  mkdir -p custom
  cat > "$CONTEXT_FILE"
  echo "✓ Guardado en $CONTEXT_FILE" >&2
fi

CONTEXT=$(cat "$CONTEXT_FILE")
echo "🤖 Generando configuración con $MODE..." >&2

PROMPT="Eres un experto en marketing educativo y redes sociales.

Crea un YAML para un post de Instagram. Solo YAML, sin explicaciones.

Claves:
- title: título llamativo (max 40 chars)
- tagline: frase corta (max 60 chars)
- body: texto con \n para saltos (max 200 chars)
- features: 4 items con icon (emoji), title, desc
- cta_text: texto del botón
- hashtags: separados por espacios

Contexto del proyecto:
---
$CONTEXT
---

YAML:"

GENERATED=""
TIMEOUT=30
RUN_AI() {
  local tool="$1"; shift
  command -v "$tool" >/dev/null 2>&1 || return 1
  if command -v timeout >/dev/null 2>&1; then
    echo "$PROMPT" | timeout $TIMEOUT "$tool" "$@" 2>/dev/null || return 1
  else
    echo "$PROMPT" | "$tool" "$@" 2>/dev/null || return 1
  fi
}

case "$MODE" in
  opencode) GENERATED=$(RUN_AI opencode) ;;
  gemini)   GENERATED=$(RUN_AI gemini) ;;
  codex)    GENERATED=$(RUN_AI codex) ;;
  claude)   GENERATED=$(RUN_AI claude) ;;
esac

if [ -n "$GENERATED" ]; then
  mkdir -p custom
  echo "$GENERATED" > custom/config.generated.yaml
  echo "✓ Configuración generada por $MODE" >&2
  python3 post.py
else
  echo "⚠️  No se pudo generar con IA. Pasando a modo manual." >&2
  python3 post.py --interactive
fi
