#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE_FILE="custom/.mode"

command -v python3 >/dev/null 2>&1 || { echo "❌ Necesitas Python 3" >&2; exit 1; }

SET_MODE=""
OVERRIDE_MODE=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai) OVERRIDE_MODE="$2"; shift 2 ;;
    --ai=*) OVERRIDE_MODE="${1#*=}"; shift ;;
    --modo) SET_MODE="$2"; shift 2 ;;
    --modo=*) SET_MODE="${1#*=}"; shift ;;
    -m) SET_MODE="$2"; shift 2 ;;
    --stock) EXTRA_ARGS+=("--stock" "$2"); shift 2 ;;
    --layout) EXTRA_ARGS+=("--layout" "$2"); shift 2 ;;
    --diagram) EXTRA_ARGS+=("--diagram" "$2"); shift 2 ;;
    --aspect) EXTRA_ARGS+=("--aspect" "$2"); shift 2 ;;
    --anti-slop|--lint) python3 anti_slop.py config.yaml; exit 0 ;;
    *) EXTRA_ARGS+=("$1"); shift ;;
  esac
done

# Validar modo de asistente
VALID_MODES="manual opencode freebuff antigravity gemini codex claude"
validate_mode() {
  for m in $VALID_MODES; do
    [ "$m" = "$1" ] && return 0
  done
  return 1
}

choose_mode() {
  echo "" >&2
  echo "🎨 ¿Cómo quieres generar tu post de Instagram?" >&2
  echo "" >&2
  echo "  1) Manual / Directo — Renderiza desde config.yaml con opciones CLI" >&2
  echo "  2) opencode — Asistente de IA de terminal" >&2
  echo "  3) freebuff — Asistente de IA libre para desarrollo" >&2
  echo "  4) Antigravity — Pair programmer / IDE Agent de Google DeepMind" >&2
  echo "  5) Gemini CLI — IA de Google" >&2
  echo "  6) Codex CLI — IA de OpenAI" >&2
  echo "  7) Claude CLI — IA de Anthropic" >&2
  echo "" >&2
  read -p $'\e[1mElige (1-7) [1]:\e[0m ' choice
  choice="${choice:-1}"
  case "$choice" in
    2) echo "opencode" ;;
    3) echo "freebuff" ;;
    4) echo "antigravity" ;;
    5) echo "gemini" ;;
    6) echo "codex" ;;
    7) echo "claude" ;;
    *) echo "manual" ;;
  esac
}

# Guardar modo predeterminado
if [ -n "$SET_MODE" ]; then
  if validate_mode "$SET_MODE"; then
    mkdir -p custom
    echo "$SET_MODE" > "$MODE_FILE"
    echo "✓ Modo cambiado a: $SET_MODE" >&2
    exit 0
  else
    echo "❌ Modo inválido: $SET_MODE" >&2
    echo "   Válidos: manual, opencode, freebuff, antigravity, gemini, codex, claude" >&2
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

echo "📋 Modo: $MODE    (cambia con: --modo manual|opencode|freebuff|antigravity|gemini|claude)" >&2

# ── Fuentes + Verificación ─────────────────────────────────
if [ ! -d "fonts" ] || [ ! -f "fonts/Outfit-Bold.ttf" ]; then
  echo "📥 Descargando fuentes tipográficas (Outfit Bold / Regular)..." >&2
  mkdir -p fonts
  python3 -c "
import urllib.request, os
fonts = {
  'Outfit-Bold.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4deyC4E.ttf',
  'Outfit-Regular.ttf': 'https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4TC1C4E.ttf',
}
for name, url in fonts.items():
  p = os.path.join('fonts', name)
  if not os.path.exists(p):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
      with open(p, 'wb') as f:
        f.write(resp.read())
    print(f'  ✓ {name} descargado')
" 2>/dev/null || echo "⚠️  No se pudieron descargar fuentes de Google. Se usarán fuentes del sistema." >&2
fi

# ── Modo Directo / Manual ─────────────────────────────────
if [ "$MODE" = "manual" ]; then
  python3 post.py "${EXTRA_ARGS[@]}"
  exit 0
fi

# ── Modo Antigravity ──────────────────────────────────────
if [ "$MODE" = "antigravity" ]; then
  echo "" >&2
  echo "🚀 [Antigravity Mode]" >&2
  echo "Estás en el entorno de Antigravity. Pídele directamente en el chat:" >&2
  echo "  - 'Crea un post para Instagram sobre X con layout diagram y mi logo'" >&2
  echo "  - 'Busca una foto libre en Openverse sobre educación y ponle texto'" >&2
  echo "  - 'Revisa que el copy cumpla las reglas Anti-IA Slop'" >&2
  echo "" >&2
  python3 post.py "${EXTRA_ARGS[@]}"
  exit 0
fi

# ── Modo IA (opencode, freebuff, gemini, claude, codex) ────
CONTEXT_FILE="custom/context.md"
PROMPT_FILE="custom/prompt.md"

if [ ! -f "$CONTEXT_FILE" ]; then
  echo "" >&2
  echo "📝 Describe tu proyecto o el objetivo del post (luego Ctrl+D):" >&2
  echo "" >&2
  mkdir -p custom
  cat > "$CONTEXT_FILE"
  echo "✓ Contexto guardado en $CONTEXT_FILE" >&2
fi

CONTEXT=$(cat "$CONTEXT_FILE")

# Generar prompt riguroso con reglas Anti-IA Slop
cat > "$PROMPT_FILE" << PROMPTEND
Eres un director de arte y redactor publicitario de élite. Tu objetivo es generar el archivo de configuración YAML para un post de Instagram de alto impacto.

REGLAS ESTRICTAS ANTI-IA SLOP (OBLIGATORIAS):
1. PROHIBIDO usar lenguaje publicitario inflado o clichés de IA:
   - NO uses: "revoluciona", "en el vertiginoso mundo", "en la era digital", "desbloquea el poder", "un mundo de posibilidades", "sin precedentes", "de vanguardia", "game-changer", "delve", "tapestry".
2. Sé directo, conciso, humano y específico. Usa verbos enérgicos y hechos demostrables.
3. Elige el layout visual idóneo según el caso:
   - 'card': si hay 3 o 4 características destacadas.
   - 'diagram': si hay una arquitectura o esquema técnico (con Excalidraw).
   - 'minimal': para reflexiones profundas o lemas contundentes con diseño suizo.
   - 'split': si hay una imagen/diagrama protagonista arriba y texto abajo.
   - 'quote': para testimonios o citas memorables.
4. Si buscas foto de fondo libre de derechos (Openverse), añade la clave 'stock: { query: "...", overlay: "dark" }'.
5. Responde ÚNICAMENTE con el bloque YAML válido, sin introducciones ni despedidas.

ESTRUCTURA DEL YAML ESPERADO:
title: "Título contundente (máx 40 caracteres)"
tagline: "Subtítulo claro que aporte contexto (máx 60 caracteres)"
category: "TEMA EN MAYÚSCULAS"
body: "Cuerpo del mensaje conciso, 2 o 3 líneas con información real."
features: # Solo si usas layout 'card' o 'split'
  - icon: "🎯"
    title: "Punto 1"
    desc: "Descripción concreta"
cta_text: "tuweb.es o enlace corto"
hashtags: "#Tema1 #Tema2 #Tema3"
layout: "card" # card | diagram | minimal | split | quote
aspect: "1:1"  # 1:1 o 4:5
colors:
  primary: "#hex"
  primary_dark: "#hex"
  gradient_top: "#hex"
  gradient_bottom: "#hex"

Contexto del proyecto:
---
$CONTEXT
---
PROMPTEND

echo "" >&2
echo "✅ Prompt Anti-IA Slop generado en $PROMPT_FILE" >&2

# Si la herramienta está disponible, ejecutarla
if [ "$MODE" = "freebuff" ] && command -v freebuff >/dev/null 2>&1; then
  echo "🤖 Ejecutando Freebuff..." >&2
  freebuff --trust-agents
  exit 0
elif [ "$MODE" = "opencode" ] && command -v opencode >/dev/null 2>&1; then
  echo "🤖 Ejecutando OpenCode..." >&2
  opencode run "Lee custom/prompt.md y genera custom/config.generated.yaml siguiendo las reglas Anti-IA Slop."
  python3 post.py "${EXTRA_ARGS[@]}"
  exit 0
elif command -v "$MODE" >/dev/null 2>&1; then
  echo "🤖 Ejecutando $MODE..." >&2
  (cat "$PROMPT_FILE"; cat) | "$MODE"
else
  echo "" >&2
  echo "💡 Copia $PROMPT_FILE en tu asistente IA preferido ($MODE)." >&2
  echo "   Guarda la salida en custom/config.generated.yaml y ejecuta:" >&2
  echo "   python3 post.py" >&2
fi
