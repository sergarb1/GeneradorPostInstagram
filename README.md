# GeneradorPostInstagram 2.0 🖼️📐🤖

**Genera imágenes promocionales de alto impacto para Instagram (1080×1080 y 1080×1350) desde la terminal o mediante asistentes de IA.**

Diseñado desde cero para trabajar mano a mano con **Antigravity**, **OpenCode**, **Freebuff**, **Claude** y **Gemini CLI**.

100% Gratuito · Código Abierto (AGPL v3) · Python + Pillow + CairoSVG · Bancos Libres · Excalidraw · Anti-IA Slop

---

## ⚡ Novedades de la Versión 2.0

- 📸 **Bancos de Imágenes Libres Integrados:** Búsqueda y descarga automática desde la API abierta de **Openverse** (Creative Commons y Dominio Público de WordPress Foundation) y **Wikimedia Commons**. Cero claves de API, con recorte inteligente y capas de contraste (*scrim*) automáticas.
- 📐 **Soporte Nativo para Excalidraw:** Integra diagramas de arquitectura, flujos o bocetos técnicos exportados en **SVG** o **PNG** con renderizado vectorial de alta resolución y marco de blueprint técnico.
- 🛡️ **Motor y Linter Anti-IA Slop:** Filtro activo de calidad que detecta clichés vacíos de IA (*"revoluciona"*, *"en el vertiginoso mundo"*, *"desbloquea"*), elimina el exceso de emojis y promueve un diseño editorial honesto y limpio.
- 🏷️ **Gestión Avanzada de Logos de Marca:** Admite logos en formato vectorial **SVG** o raster **PNG/WebP** con canal alfa, pastilla protectora de cristal esmerilado (*frosted glass pill*) y **extracción automática de paleta cromática corporativa**.
- 🎨 **Múltiples Layouts y Ratios:** Diseños especializados (`card`, `diagram`, `minimal`, `split`, `quote`) y formatos optimizados para Instagram Feed (`1:1` cuadrado y `4:5` portrait vertical).

---

## 🚀 Inicio Rápido (30 segundos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/sergarb1/GeneradorPostInstagram.git
cd GeneradorPostInstagram

# 2. Generar el post por defecto
./generate.sh
```

El post se generará en milisegundos en `output/post.png`.

---

## 🎨 Galería de Layouts

El generador incluye 5 layouts visuales seleccionables mediante `layout:` en `config.yaml` o mediante el flag `--layout`:

| Layout | Aspecto | Descripción | Caso de Uso |
|---|---|---|---|
| **`card`** | `1:1` o `4:5` | Tarjeta flotante moderna con glassmorphism, badge de categoría, titular y hasta 4 características con iconos. | Anuncios de proyectos, cursos, lanzamientos de productos. |
| **`diagram`** | `1:1` | Ventana técnica central tipo blueprint con controles de terminal, titular superior y conclusiones al pie. | Arquitecturas cloud, flujos de software, esquemas de Excalidraw. |
| **`minimal`** | `4:5` | Estilo editorial suizo de alto contraste, titular tipográfico dominante, generoso espacio negativo y elegancia pura. | Manifiestos, lemas de marca, ideas contundentes sin ruido visual. |
| **`split`** | `1:1` | Pantalla dividida: mitad superior visual (diagrama o foto de stock) y mitad inferior informativa. | Comparativas, casos de estudio, resúmenes con soporte gráfico. |
| **`quote`** | `1:1` o `4:5` | Comillas tipográficas gigantes, texto central destacado, cita de autor y marca de agua inferior. | Citas inspiradoras, testimonios reales de usuarios o clientes. |

---

## 🤖 Flujo de Trabajo con OpenCode, Freebuff o Antigravity

El sistema está pensado para que abras tu asistente en este directorio y trabajes en 2 pasos naturales:

### 1. "Configura mi plantilla con este logo"
Le dices a tu asistente (OpenCode, Freebuff o Antigravity):
> *"Este es mi logo: custom/logo.svg, hazme una plantilla de marca."*

El asistente ejecuta `python3 brand_logo.py <logo> --setup-template "Nombre"`. El sistema:
- Extrae la paleta cromática de tu logo (primario, oscuro, acento pastel y degradados).
- Guarda la identidad corporativa en `custom/brand_template.yaml`.
- Configura el logo con pastilla protectora de cristal esmerilado (*frosted glass pill*).

### 2. "Hazme posts sobre cualquier tema con mi plantilla"
A partir de ahí, solo le pides posts sobre lo que necesites:
> *"Hazme un post sobre cómo desplegar Docker con mi diagrama de Excalidraw custom/diagram.svg"*  
> *"Hazme un post sobre educación con foto de Openverse en layout minimal (4:5)"*

El asistente:
1. Aplica las **reglas estrictas Anti-IA Slop** (lenguaje directo, datos reales, cero clichés).
2. Escribe únicamente el nuevo contenido en `custom/config.local.yaml`.
3. El motor **hereda automáticamente tu plantilla de marca** (`custom/brand_template.yaml`), manteniendo tu logo y tus colores corporativos.
4. Ejecuta `python3 post.py` y te entrega el post final listo en `output/post.png`.

---

## 📸 Bancos de Imágenes Libres (Openverse / Wikimedia)

Puedes buscar fotos de fondo en lenguaje natural directamente desde la configuración o por terminal:

### En `config.yaml`:
```yaml
stock:
  query: "minimalist architecture modern"
  overlay: "dark"    # dark (scrim de alto contraste) | light | vignette | none
  blur: 0            # 0 para nítido, 1 a 10 para desenfoque gaussiano suave
```

### Por Terminal (CLI):
```bash
./generate.sh --stock "workspace clean laptop" --layout split
```

El script descarga la foto de la API abierta de Openverse, realiza un recorte inteligente al ratio de tu post y aplica una capa de contraste para que el texto sea perfectamente legible según la norma WCAG AAA.

---

## 📐 Diagramas con Excalidraw

1. Dibuja tu arquitectura o diagrama en [excalidraw.com](https://excalidraw.com).
2. Pulsa `Ctrl + Shift + E` (Exportar imagen) y guárdalo como **SVG** o **PNG**.
3. Cópialo en `custom/diagram.svg`.
4. Ejecuta:
   ```bash
   ./generate.sh --diagram custom/diagram.svg --layout diagram
   ```

El motor utilizará `CairoSVG` para renderizar vectores con nitidez Retina y los encuadrará en una tarjeta de alta fidelidad técnica.

---

## 🛡️ Motor Anti-IA Slop

Cansados de los posts que suenan a robot (*"En el vertiginoso mundo de la era digital, desbloquea el poder revolucionario..."*), el proyecto incorpora un linter estricto de calidad:

```bash
# Validar la honestidad y calidad de tu texto:
python3 anti_slop.py config.yaml
```

- **Bloquea clichés publicitarios:** Prohíbe adjetivos vacíos e hipérboles comunes de ChatGPT.
- **Limita el exceso de emojis:** Favorece números ordinales elegantes (`01`, `02`) y diseño editorial.
- **Verifica contrastes de color:** Analiza la luminancia entre fondo y texto para garantizar accesibilidad.

---

## 🏷️ Logos de Marca y Extracción de Color

Coloca tu logo corporativo en `custom/logo.svg` o `custom/logo.png`:

```yaml
logo:
  path: "custom/logo.svg"
  position: "top-right"      # top-right | top-left | bottom-right | bottom-left | center-top
  height: 55                 # Altura en píxeles
  badge: true                # Pastilla de cristal esmerilado para aislar el logo de fondos oscuros
  extract_palette: true      # Deriva automáticamente la paleta del post desde los colores del logo
```

---

## ⚙️ Referencia de Configuración (`config.yaml`)

```yaml
title: "Mejora tu Docencia"
tagline: "Estrategias y herramientas abiertas para transformar el aula"
category: "EDUCACIÓN ABIERTA"
body: "Plataforma comunitaria de recursos pedagógicos verificados por docentes en activo."

features:
  - icon: "🎯"
    title: "100% Gratuito"
    desc: "Sin barreras de registro ni publicidad"
  - icon: "🤝"
    title: "Colaborativo"
    desc: "Creado por y para docentes"

cta_text: "mejoratudocencia.es"
hashtags: "#EducaciónLibre #Docencia #Innovacion"

layout: "card"        # card | diagram | minimal | split | quote
aspect: "1:1"         # 1:1 (1080x1080) | 4:5 (1080x1350 feed) | 9:16 (1080x1920 story)

colors:
  primary: "#16a34a"
  primary_dark: "#14532d"
  gradient_top: "#15803d"
  gradient_bottom: "#052e16"
  card_bg: "#ffffffeb"
  text_body: "#334155"
  text_light: "#64748b"
  accent_light: "#bbf7d0"
```

---

## 💻 Requisitos e Instalación

### Dependencias del Sistema
- Python 3.9+
- Librería Cairo (para SVG):
  - **Linux (Debian/Ubuntu):** `sudo apt install libcairo2 libcairo2-dev`
  - **macOS:** `brew install cairo`
  - **Windows:** Incluido en paquetes o automático.

### Dependencias de Python
```bash
pip install -r requirements.txt
```

---

## 📚 Documentación Adicional

- [AGENTS.md](file:///home/sergi/Escritorio/GeneradorPostInstagram/AGENTS.md) — Manual exhaustivo para Asistentes y Agentes de Código Autónomos (Antigravity, OpenCode, Freebuff, Claude).
- [HANDSOFF.md](file:///home/sergi/Escritorio/GeneradorPostInstagram/HANDSOFF.md) — Manual de operaciones, traspaso de proyecto, mantenimiento y solución de problemas.

---

## 📄 Licencia

**GNU AGPL v3** — Software libre y abierto. Puedes usarlo, mejorarlo y compartirlo libremente.
