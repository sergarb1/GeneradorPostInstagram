#!/usr/bin/env python3
"""
ai_support.py — Puente de Asistencia de IA (OpenCode, Freebuff, Antigravity, Claude, Gemini)
Diseñado para actuar como el canal de soporte inteligente del generador de posts.
Construye el contexto con directrices Anti-IA Slop, detecta diagramas de Excalidraw,
logos de marca e imágenes de stock, e invoca al asistente de IA elegido para generar
el archivo declarativo YAML y renderizar el post final.
"""

import os
import sys
import re
import subprocess
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
CUSTOM_DIR = os.path.join(ROOT, "custom")
OUTPUT_DIR = os.path.join(ROOT, "output")
PROMPT_FILE = os.path.join(CUSTOM_DIR, "prompt.md")
CONTEXT_FILE = os.path.join(CUSTOM_DIR, "context.md")
GENERATED_CONFIG = os.path.join(CUSTOM_DIR, "config.generated.yaml")

ANTI_SLOP_PROMPT_TEMPLATE = """Eres el Director de Arte y Redactor Publicitario de este post de Instagram.
Tu misión es diseñar un post honesto, de altísimo impacto visual y libre de clichés.

REGLAS OBLIGATORIAS ANTI-IA SLOP:
1. PROHIBIDO usar clichés publicitarios típicos de LLMs:
   - NUNCA uses: "revoluciona", "en el vertiginoso mundo", "en la era digital", "desbloquea el poder", "un mundo de posibilidades", "sin precedentes", "de vanguardia", "game-changer", "delve", "tapestry", "testament", "unleash", "elevate".
2. Tono humano, conciso y técnico: Emplea verbos directos y datos concretos.
3. Máximo 1 emoji contextual por característica. Nunca uses emojis como viñetas decorativas sin sentido.

RECURSOS DISPONIBLES EN EL PROYECTO:
{resources_detected}

LAYOUTS DISPONIBLES (Elige el más adecuado según el contenido):
- 'card': Para 3 o 4 características o beneficios estructurados.
- 'diagram': Si hay un esquema técnico o arquitectura de software (con Excalidraw en SVG/PNG).
- 'minimal': Estilo editorial suizo de alto contraste (ideal en ratio 4:5 portrait).
- 'split': Mitad superior visual (diagrama o foto de stock) y mitad inferior con contenido.
- 'quote': Para citas memorables, aprendizajes clave o testimonios.

BANCOS DE IMÁGENES LIBRES (Openverse / Wikimedia):
Si el post requiere fotografía de fondo, incluye la clave:
stock:
  query: "descripción en lenguaje natural para Openverse"
  overlay: "dark" # dark | light | vignette

PETICIÓN DEL USUARIO / TEMA:
"{user_request}"

{project_context}

INSTRUCCIÓN FINAL:
Responde ÚNICAMENTE con el bloque YAML válido entre ```yaml y ``` (sin explicaciones adicionales antes ni después).

ESTRUCTURA EXACTA DEL YAML REQUERIDO:
```yaml
title: "Título contundente (máx. 40 caracteres)"
tagline: "Subtítulo descriptivo que aporte contexto (máx. 60 caracteres)"
category: "TEMA PRINCIPAL EN MAYÚSCULAS"
body: "Cuerpo explicativo directo de 2 a 3 líneas con información sustancial."
features: # Solo si usas layout 'card' o 'split'
  - icon: "🎯"
    title: "Punto 1"
    desc: "Descripción concreta y verificable"
cta_text: "enlace.com o acción concreta"
hashtags: "#Tema1 #Tema2 #Tema3"
layout: "{suggested_layout}" # card | diagram | minimal | split | quote
aspect: "1:1"  # 1:1 (1080x1080) o 4:5 (1080x1350)
colors:
  primary: "#hex"
  primary_dark: "#hex"
  gradient_top: "#hex"
  gradient_bottom: "#hex"
  accent_light: "#hex"
```
"""

def detect_project_resources() -> dict:
    """Inspecciona la carpeta custom/ para detectar logos, diagramas y contextos existentes."""
    res = {
        "logo": None,
        "diagram": None,
        "context": None,
        "notes": []
    }

    # Detectar logo
    for ext in (".svg", ".png", ".webp"):
        p = os.path.join(CUSTOM_DIR, f"logo{ext}")
        if os.path.exists(p):
            res["logo"] = f"custom/logo{ext}"
            res["notes"].append(f"- Logo corporativo detectado: {res['logo']} (añade 'logo: {res['logo']}')")
            break

    # Detectar diagrama de Excalidraw
    for name in ("diagram.svg", "diagram.png", "test_diagram.svg"):
        p = os.path.join(CUSTOM_DIR, name)
        if os.path.exists(p):
            res["diagram"] = f"custom/{name}"
            res["notes"].append(f"- Diagrama de Excalidraw disponible: {res['diagram']} (recomendado layout: diagram)")
            break

    # Detectar contexto
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            res["context"] = f.read().strip()
            res["notes"].append("- Contexto del proyecto cargado desde custom/context.md")

    return res

def build_prompt(user_request: str) -> str:
    """Construye el prompt Anti-IA Slop enriquecido con los recursos detectados."""
    resources = detect_project_resources()
    resources_str = "\n".join(resources["notes"]) if resources["notes"] else "- Sin archivos multimedia previos en custom/"

    context_str = ""
    if resources["context"]:
        context_str = f"CONTEXTO DEL PROYECTO:\n---\n{resources['context']}\n---"

    suggested_layout = "diagram" if resources["diagram"] else "card"

    return ANTI_SLOP_PROMPT_TEMPLATE.format(
        resources_detected=resources_str,
        user_request=user_request or "Crea un post promocional atractivo y profesional",
        project_context=context_str,
        suggested_layout=suggested_layout
    )

def extract_yaml_from_response(text: str) -> str:
    """Extrae el contenido YAML limpio de una respuesta que contenga bloques markdown."""
    match = re.search(r"```(?:yaml)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def run_ai_support(provider: str, user_request: str, execute_now: bool = False):
    """
    Prepara la integración de IA de apoyo (OpenCode, Freebuff, Claude, Gemini).
    Si execute_now=False (por defecto), prepara el entorno, archivos de prompt y muestra el comando exacto.
    Si execute_now=True, lanza el proceso CLI.
    """
    os.makedirs(CUSTOM_DIR, exist_ok=True)
    prompt_text = build_prompt(user_request)

    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    print("=" * 65)
    print(f"🤖 GENERADOR POST INSTAGRAM — SOPORTE DE IA ({provider.upper()})")
    print("=" * 65)
    print(f"📝 Prompt Anti-IA Slop preparado en: {PROMPT_FILE}")

    if provider == "opencode":
        print("\nPara que OpenCode genere el post con soporte autónomo, ejecuta:")
        print(f"  opencode run --pure --auto \"Lee custom/prompt.md y escribe el YAML en {GENERATED_CONFIG}\"")
        print("\nO en modo interactivo:")
        print("  opencode")
        if execute_now:
            print("🚀 Ejecutando OpenCode...")
            cmd = ["opencode", "run", "--pure", "--auto", f"Lee custom/prompt.md y guarda solo el YAML en {GENERATED_CONFIG}"]
            subprocess.run(cmd, cwd=ROOT)

    elif provider == "freebuff":
        print("\nPara ejecutar Freebuff con soporte de agentes:")
        print("  freebuff --trust-agents")
        print("  (Copia o referencia el contenido de custom/prompt.md)")
        if execute_now:
            subprocess.run(["freebuff", "--trust-agents"], cwd=ROOT)

    elif provider == "antigravity":
        print("\nPara usar Antigravity:")
        print("  Simplemente pídele en el chat de Antigravity:")
        print(f"  'Genera el post con el contexto de custom/prompt.md'")

    elif provider in ("claude", "gemini", "codex"):
        print(f"\nPara ejecutar con {provider} CLI:")
        print(f"  cat custom/prompt.md | {provider}")
        if execute_now and subprocess.run(["which", provider], capture_output=True).returncode == 0:
            p = subprocess.Popen([provider], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            out, _ = p.communicate(input=prompt_text)
            clean_yaml = extract_yaml_from_response(out)
            with open(GENERATED_CONFIG, "w", encoding="utf-8") as f:
                f.write(clean_yaml)
            print(f"💾 Configuración guardada en: {GENERATED_CONFIG}")

    print("\nUna vez generado custom/config.generated.yaml, renderiza con:")
    print("  python3 post.py")
    print("=" * 65)

if __name__ == "__main__":
    provider_arg = "opencode"
    request_arg = ""
    do_exec = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("--ai", "--provider") and i + 1 < len(args):
            provider_arg = args[i+1]
            i += 2
        elif args[i] == "--execute":
            do_exec = True
            i += 1
        else:
            request_arg += " " + args[i]
            i += 1

    run_ai_support(provider_arg, request_arg.strip(), execute_now=do_exec)
