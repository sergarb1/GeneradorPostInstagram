#!/usr/bin/env python3
"""
anti_slop.py — Motor de Calidad Anti-IA Slop
Detecta clichés, lenguaje inflado, frases vacías típicas de LLMs y valida
contraste y jerarquía visual para posts honestos, directos y profesionales.
"""

import re
import sys
import yaml

# Clichés y palabras vacías típicas de IA generativa (Español e Inglés)
SLOP_PATTERNS = [
    # Español - Frases infladas y vacías
    (r"\brevoluciona\b", "revoluciona", "Usa verbos concretos: 'mejora', 'acelera', 'organiza' o explica qué hace exactamente."),
    (r"\ben el vertiginoso mundo\b", "en el vertiginoso mundo", "Evita introducciones melodramáticas."),
    (r"\ben la era digital\b", "en la era digital", "Cliché innecesario, ve directo al grano."),
    (r"\bdesbloquea(r)?\b", "desbloquea", "Demasiado publicitario tipo SaaS genérico. Usa 'accede a', 'aprende' o 'descarga'."),
    (r"\bun mundo de posibilidades\b", "un mundo de posibilidades", "Frase comodín vacía."),
    (r"\bsin precedentes\b", "sin precedentes", "Hipérbole poco creíble."),
    (r"\bel poder de\b", "el poder de", "Cliché gastado. Describe la utilidad real."),
    (r"\ba la vanguardia\b", "a la vanguardia", "Palabrería corporativa."),
    (r"\bsumérgete\b", "sumérgete", "Típico cliché de IA turística o de copywriting barato."),
    (r"\bdeléitate\b", "deléitate", "Tono excesivamente artificial."),
    (r"\btestimonio de\b", "testimonio de", "Traducción literal de 'a testament to'."),
    (r"\bun tapiz de\b", "un tapiz de", "Traducción literal de 'a tapestry of'."),
    (r"\bsin esfuerzo\b", "sin esfuerzo", "Promesa irreal. Sé honesto sobre el flujo de trabajo."),
    (r"\bde vanguardia\b", "de vanguardia", "Adjetivo vacío."),
    (r"\bjuego-cambiador\b", "juego-cambiador", "Calco de game-changer."),
    (r"\bpotencia tus\b", "potencia tus", "Usa términos precisos."),
    
    # Inglés - Classic AI slop
    (r"\bdelve\b", "delve", "Classic ChatGPT giveaway. Use 'explore', 'examine', or 'analyze'."),
    (r"\btapestry\b", "tapestry", "Overused AI metaphor."),
    (r"\btestament\b", "testament", "Overused AI flourish."),
    (r"\bunleash\b", "unleash", "Over-hyped marketing jargon."),
    (r"\brevolutionize\b", "revolutionize", "Unrealistic hype."),
    (r"\bgame-changer\b", "game-changer", "Hollow buzzword."),
    (r"\bparadigm shift\b", "paradigm shift", "Corporate jargon."),
    (r"\belevate\b", "elevate", "Overused SaaS buzzword."),
    (r"\bseamlessly\b", "seamlessly", "Overused AI adverb. Be specific."),
    (r"\bin today's fast-paced\b", "in today's fast-paced", "Tiresome boilerplate opener."),
]

def analyze_text(text: str) -> list[dict]:
    """Analiza una cadena de texto en busca de clichés de IA slop."""
    findings = []
    if not text:
        return findings

    for pattern, keyword, suggestion in SLOP_PATTERNS:
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for m in matches:
            findings.append({
                "keyword": keyword,
                "matched": m.group(0),
                "suggestion": suggestion,
                "start": m.start(),
                "end": m.end()
            })
    return findings

def lint_config(cfg: dict) -> dict:
    """Evalúa todo el contenido textual de una configuración de post."""
    issues = []
    texts_to_check = [
        ("title", cfg.get("title", "")),
        ("tagline", cfg.get("tagline", "")),
        ("body", cfg.get("body", "")),
        ("cta_text", cfg.get("cta_text", "")),
    ]

    for feat in cfg.get("features", []):
        if isinstance(feat, dict):
            texts_to_check.append(("feature.title", feat.get("title", "")))
            texts_to_check.append(("feature.desc", feat.get("desc", "")))

    for field, content in texts_to_check:
        results = analyze_text(content)
        for r in results:
            issues.append({
                "field": field,
                "matched": r["matched"],
                "suggestion": r["suggestion"]
            })

    # Detección de sobreabundancia de emojis en el body (más de 4 emojis suele denotar IA slop)
    body = cfg.get("body", "")
    emoji_count = len(re.findall(r"[\U00010000-\U0010ffff]", body))
    if emoji_count > 4:
        issues.append({
            "field": "body",
            "matched": f"{emoji_count} emojis",
            "suggestion": "Demasiados emojis en el cuerpo. Reduce a 0-2 para una estética profesional y limpia."
        })

    is_clean = len(issues) == 0
    score = max(0, 100 - len(issues) * 20)

    return {
        "clean": is_clean,
        "score": score,
        "issues": issues
    }

def calculate_luminance(hex_color: str) -> float:
    """Calcula la luminancia relativa según la fórmula WCAG."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 8:
        hex_color = hex_color[:6]
    elif len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

def contrast_ratio(hex_fg: str, hex_bg: str) -> float:
    """Calcula el ratio de contraste entre dos colores hex (1 a 21)."""
    l1 = calculate_luminance(hex_fg)
    l2 = calculate_luminance(hex_bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def print_report(lint_res: dict):
    """Muestra un informe visual legible en terminal."""
    print("=" * 60)
    print("🛡️  INFORME ANTI-IA SLOP")
    print("=" * 60)
    if lint_res["clean"]:
        print("✅ ¡Excelente! El texto es directo, creíble y libre de clichés de IA.")
        print(f"   Puntuación de honestidad: {lint_res['score']}/100")
    else:
        print(f"⚠️  Se detectaron {len(lint_res['issues'])} patrones de cliché o relleno artificial.")
        print(f"   Puntuación de honestidad: {lint_res['score']}/100\n")
        for i, issue in enumerate(lint_res["issues"], 1):
            print(f"  {i}. Campo [{issue['field']}]: encontró '{issue['matched']}'")
            print(f"     💡 Sugerencia: {issue['suggestion']}\n")
    print("=" * 60)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        res = lint_config(data)
        print_report(res)
        if not res["clean"] and "--strict" in sys.argv:
            sys.exit(1)
    except Exception as e:
        print(f"Error analizando {target}: {e}")
        sys.exit(1)
