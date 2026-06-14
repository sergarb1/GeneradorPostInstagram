# GeneradorPostInstagram 🖼️🤖

**Crea posts promocionales para Instagram desde la terminal. Funciona solo o con apoyo de IA (opencode, Gemini CLI, Codex, Claude).**

100% Gratuito · Código abierto (AGPL v3) · Python + Pillow · Sin servidor

---

## 🚀 Uso rápido

```bash
git clone https://github.com/sergarb1/GeneradorPostInstagram.git
cd GeneradorPostInstagram
./generate.sh
```

Esto genera `output/post.png` — un PNG 1080×1080 listo para Instagram.

---

## ✨ Cómo funciona

### 1. Sin IA (configuración manual)

Edita `config.yaml` con los datos de tu proyecto:

```yaml
title: "Mejora tu Docencia"
tagline: "Recursos gratuitos para innovar en el aula"
features:
  - icon: "🎯"
    title: "100% Gratuito"
    desc: "Sin coste, sin registro, sin publicidad"
cta_text: "mejoratudocencia.es"
hashtags: "#Educación #Docentes #Gratuito"
colors:
  primary: "#16a34a"
  gradient_top: "#16a34a"
  gradient_bottom: "#052e16"
```

### 2. Con IA (generación automática)

Escribe el contexto de tu proyecto en `custom/context.md`:

```markdown
# Mi Proyecto
App educativa gratuita para docentes.
Público: profesores de secundaria.
Tono: cercano e inspirador.
Valores: gratuito, colaborativo, código abierto.
```

Y ejecuta:

```bash
./generate.sh --ai opencode
```

La IA lee el contexto, genera el `config.yaml` automáticamente y produce el post.

### 3. Layout personalizado (IA de imágenes)

Genera un fondo con DALL·E, Midjourney o cualquier IA y úsalo de base:

```yaml
background: "custom/mi_layout.png"
```

Coloca la imagen en `custom/` (gitignored), el texto se superpone automáticamente.

### 4. Personalización avanzada

La carpeta `custom/` (gitignored) puede contener:

| Archivo | Propósito |
|---------|-----------|
| `custom/context.md` | Descripción del proyecto para la IA |
| `custom/logo.png` | Logo que aparece en el post |
| `custom/config.local.yaml` | Sobreescribe valores de `config.yaml` |
| `custom/config.generated.yaml` | Config generada por el modo interactivo o IA |
| `custom/mi_layout.png` | Imagen de fondo generada por IA (DALL·E, Midjourney...) |

---

## 🤖 Herramientas de IA soportadas

| Herramienta | Comando |
|-------------|---------|
| **opencode** | `./generate.sh --ai opencode` |
| **Gemini CLI** | `./generate.sh --ai gemini` |
| **OpenAI Codex CLI** | `./generate.sh --ai codex` |
| **Claude CLI** | `./generate.sh --ai claude` |

Si la herramienta no está instalada o no hay `custom/context.md`, usa la configuración por defecto sin IA.

---

## 🖥️ Requisitos

### Programas necesarios

| Programa | Cómo instalarlo |
|----------|----------------|
| **Python 3.8+** | [Descargar python.org](https://python.org) o `sudo apt install python3 python3-pip` (Linux), `brew install python` (Mac) |
| **pip** | Viene con Python 3.4+. Si falta: `python3 -m ensurepip --upgrade` |
| **Git** | `sudo apt install git` (Linux), `brew install git` (Mac), o [git-scm.com](https://git-scm.com) |

Verifica que todo está listo:

```bash
python3 --version && pip --version && git --version
```

### Dependencias Python

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install pillow pyyaml requests
```

### Opcional — CLIs de IA

| Herramienta | Instalación |
|-------------|-------------|
| **opencode** | `npm install -g @opencode/cli` |
| **Gemini CLI** | `pip install google-generativeai` |
| **Codex CLI** | `npm install -g @openai/codex` |
| **Claude CLI** | `npm install -g @anthropic-ai/claude` |

### Fuentes

El script `generate.sh` descarga las fuentes Outfit automáticamente al ejecutarse. No hace falta hacer nada.

---

## 📁 Estructura del proyecto

```
GeneradorPostInstagram/
├── post.py              # Generador principal (Pillow)
├── config.yaml          # Configuración del post
├── requirements.txt     # Dependencias Python
├── generate.sh          # Script Linux/Mac (descarga fuentes, instala deps, ejecuta)
├── generate.bat         # Script Windows
├── index.html           # Página web del proyecto
├── templates/
│   └── default.json     # Plantilla visual
├── custom/              # GITIGNORED — datos del usuario
│   ├── context.md       # Contexto para IA
│   ├── logo.png         # Logo personalizado
│   ├── config.local.yaml# Override manual de config.yaml
│   ├── config.generated.yaml  # Generado por --interactive o IA
│   └── layout.png       # Fondo generado por IA de imágenes
├── output/              # GITIGNORED — posts generados
├── fonts/               # GITIGNORED — fuentes descargadas
├── AGENTS.md            # Guía para asistentes IA
├── README.md
└── LICENSE              # AGPL v3
```

---

## 🌐 Despliegue web

El proyecto incluye un `index.html` que puedes servir como landing page:

```bash
python -m http.server 8000
# Abre http://localhost:8000
```

O súbelo a GitHub Pages, Netlify, Vercel, etc.

---

## 📄 Licencia

**GNU AGPL v3** — Usa, modifica y comparte, pero cualquier mejora o derivado debe mantenerse libre.

Esto garantiza que:
- ✅ Cualquier persona puede usar la herramienta gratis
- ✅ Si alguien la mejora, debe liberar sus cambios
- ❌ Nadie puede cerrar el código y venderlo sin publicar sus modificaciones

---

## 🧑‍💻 Contribuir

1. Fork el repo
2. Crea una rama: `git checkout -b mi-mejora`
3. Commit: `git commit -m "feat: mi mejora"`
4. Push: `git push origin mi-mejora`
5. Abre un Pull Request
