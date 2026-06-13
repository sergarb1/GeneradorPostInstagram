#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE_FILE="custom/.mode"

command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3" >&2; exit 1; }

SET_MODE=""
OVERRIDE_MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) OVERRIDE_MODE="$2"; shift 2 ;;
    --ai=*) OVERRIDE_MODE="${1#*=}"; shift ;;
    --modo) SET_MODE="$2"; shift 2 ;;
    --modo=*) SET_MODE="${1#*=}"; shift ;;
    -m) SET_MODE="$2"; shift 2 ;;
    *) echo "Uso: $0 [--ai opencode|codex|gemini|claude] [--modo manual|opencode|gemini|codex|claude]" >&2; exit 1 ;;
  esac
done

# Validar modo
VALID_MODES="manual opencode gemini codex claude"
validate_mode() {
  for m in $VALID_MODES; do
    [ "$m" = "$1" ] && return 0
  done
  return 1
}

choose_mode() {
  echo "" >&2
  echo "🎨 ¿Cómo quieres crear tu post de Instagram?" >&2
  echo "" >&2
  echo "  1) Manual — te guío paso a paso con preguntas" >&2
  echo "  2) opencode — IA conversacional (te entrevista y genera el post)" >&2
  echo "  3) Gemini CLI — IA de Google" >&2
  echo "  4) Codex CLI — IA de OpenAI" >&2
  echo "  5) Claude CLI — IA de Anthropic" >&2
  echo "" >&2
  read -p $'\e[1mElige (1-5) [1]:\e[0m ' choice
  choice="${choice:-1}"
  case "$choice" in
    2) echo "opencode" ;;
    3) echo "gemini" ;;
    4) echo "codex" ;;
    5) echo "claude" ;;
    *) echo "manual" ;;
  esac
}

# --modo establece y guarda el modo permanentemente
if [ -n "$SET_MODE" ]; then
  if validate_mode "$SET_MODE"; then
    mkdir -p custom
    echo "$SET_MODE" > "$MODE_FILE"
    echo "✓ Modo cambiado a: $SET_MODE" >&2
    exit 0
  else
    echo "❌ Modo inválido: $SET_MODE" >&2
    echo "   Válidos: manual, opencode, gemini, codex, claude" >&2
    exit 1
  fi
fi

MODE="$OVERRIDE_MODE"
if [ -z "$MODE" ]; then
  if [ ! -f "$MODE_FILE" ]; then
    mkdir -p custom
    MODE=$(choose_mode)
    echo "$MODE" > "$MODE_FILE"
    echo "✓ Modo guardado" >&2
  else
    MODE=$(cat "$MODE_FILE")
  fi
fi

echo "📋 Modo: $MODE    (cambia con: --modo manual|opencode|gemini|codex|claude)" >&2

# ── fuentes + deps ────────────────────────────────────────
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

# ── modo manual ──────────────────────────────────────────
if [ "$MODE" = "manual" ]; then
  python3 post.py --interactive
  exit 0
fi

# ── modo IA ──────────────────────────────────────────────
CONTEXT_FILE="custom/context.md"
PROMPT_FILE="custom/prompt.md"

# Pedir contexto si no existe
if [ ! -f "$CONTEXT_FILE" ]; then
  echo "" >&2
  echo "📝 Describe tu proyecto (luego Ctrl+D):" >&2
  echo "" >&2
  mkdir -p custom
  cat > "$CONTEXT_FILE"
  echo "✓ Contexto guardado en $CONTEXT_FILE" >&2
fi

CONTEXT=$(cat "$CONTEXT_FILE")

# Generar prompt para la IA
cat > "$PROMPT_FILE" << PROMPTEND
Eres un asistente experto en marketing educativo. Tu tarea es crear un post promocional para Instagram.

Tu objetivo es entrevistar al usuario para obtener la información necesaria y luego generar el archivo YAML de configuración.

IMPORTANTE: Debes mantener una conversación natural. Pregunta una cosa a la vez.
Cuando tengas toda la información, responde ÚNICAMENTE con el YAML (sin explicaciones ni código alrededor).

El YAML debe tener esta estructura:
- title: título llamativo (máx. 40 caracteres)
- tagline: frase corta de apoyo (máx. 60)
- body: texto principal con \n para saltos (máx. 200)
- features: 4 elementos con icon (emoji), title, desc
- cta_text: texto del botón (URL o texto corto)
- hashtags: separados por espacios

Contexto del proyecto del usuario:
---
$CONTEXT
---

Empieza la conversación. Saluda al usuario y pregunta qué proyecto quiere promocionar.
PROMPTEND

echo "" >&2
echo "✅ Prompt preparado en $PROMPT_FILE" >&2
echo "" >&2

echo "📤 Pasa este prompt a la IA que quieras usar:" >&2
echo "" >&2
echo "   cat $PROMPT_FILE | $MODE" >&2
echo "" >&2
echo "   O copia el contenido de $PROMPT_FILE y pégalo en tu IA favorita." >&2
echo "" >&2
echo "💡 La IA te hará preguntas. Cuando termine, te dará un YAML." >&2
echo "   Guárdalo en custom/config.generated.yaml y ejecuta:" >&2
echo "   python3 post.py" >&2
echo "" >&2

# Si la herramienta está instalada, ofrecer lanzarla
if command -v "$MODE" >/dev/null 2>&1; then
  echo "🔗 $MODE detectado. ¿Quieres lanzarlo ahora? [s/N]: " >&2
  read -r launch
  if [ "$launch" = "s" ] || [ "$launch" = "S" ]; then
    echo "" >&2
    echo "🤖 Ejecutando $MODE..." >&2
    echo "   La IA leerá el prompt y te hará preguntas." >&2
    echo "   Cuando termine, el YAML aparecerá en pantalla." >&2
    echo "   Cópialo a custom/config.generated.yaml" >&2
    echo "" >&2
    # Enviar prompt primero, luego conectar stdin para la conversación
    (cat "$PROMPT_FILE"; cat) | "$MODE"
    echo "" >&2
    echo "💡 ¿Te dio la IA el YAML? Pégalo en custom/config.generated.yaml" >&2
  fi
fi
