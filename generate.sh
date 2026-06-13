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
  echo "  2) IA — prepara un prompt para que lo uses con ChatGPT, Claude, etc." >&2
  echo "" >&2
  read -p $'\e[1mElige (1-2) [1]:\e[0m ' choice
  choice="${choice:-1}"
  case "$choice" in
    2) echo "ai" ;;
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

# ── modo IA: preparar prompt ─────────────────────────────
CONTEXT_FILE="custom/context.md"

if [ ! -f "$CONTEXT_FILE" ]; then
  echo "" >&2
  echo "📝 Describe tu proyecto en unas líneas:" >&2
  echo "   (Ctrl+D para terminar)" >&2
  echo "" >&2
  mkdir -p custom
  cat > "$CONTEXT_FILE"
  echo "✓ Guardado en $CONTEXT_FILE" >&2
fi

CONTEXT=$(cat "$CONTEXT_FILE")

PROMPT_FILE="custom/prompt.md"
cat > "$PROMPT_FILE" << PROMPT
Eres un experto en marketing educativo. Crea un archivo YAML para un post de Instagram promocional.

El YAML debe tener estas claves:
- title: título llamativo (máx. 40 caracteres)
- tagline: frase corta de apoyo (máx. 60 caracteres)
- body: texto principal, usa \\n para saltos de línea (máx. 200 caracteres)
- features: 4 elementos, cada uno con icon (emoji), title (corto), desc (una línea)
- cta_text: texto del botón (URL o texto corto)
- hashtags: separados por espacios

Reglas:
- Tono cercano, inspirador, profesional
- Responde ÚNICAMENTE con el YAML, sin explicaciones

Contexto del proyecto:
---
$CONTEXT
---

YAML:
PROMPT

echo "" >&2
echo "✅ Prompt listo en: $PROMPT_FILE" >&2
echo "" >&2
echo "📤 Pásalo a tu IA favorita:" >&2
echo "   cat $PROMPT_FILE | opencode" >&2
echo "   cat $PROMPT_FILE | gemini -" >&2
echo "   cat $PROMPT_FILE | claude -" >&2
echo "   cat $PROMPT_FILE | codex -" >&2
echo "" >&2
echo "Guarda la respuesta en custom/config.generated.yaml y ejecuta:" >&2
echo "   python3 post.py" >&2
echo "" >&2
