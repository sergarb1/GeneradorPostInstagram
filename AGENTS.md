# GeneradorPostInstagram 2.0 — AGENTS.md

> **Guía maestra para Asistentes y Agentes de Código Autónomos**  
> Diseñado específicamente para **Antigravity**, **OpenCode**, **Freebuff**, **Claude** y **Gemini CLI**.

---

## 🎯 Filosofía del Proyecto: Agent-First

Este proyecto **NO es un software monolítico ni un asistente interactivo rígido**. Es un **framework modular, declarativo y ligero** pensado para que **tú (el agente de IA)** actúes como el director de arte, redactor publicitario y ejecutor técnico del usuario.

En lugar de delegar la creatividad a un menú interactivo en la terminal que pueda fallar, **tú tienes acceso a herramientas especializadas** (búsqueda en bancos libres, renderizado de Excalidraw con CairoSVG, extracción de paletas de logos, validación anti-slop) y orquestas la generación modificando `config.yaml` o `custom/config.local.yaml` y ejecutando `post.py`.

---

## 📁 Estructura del Proyecto y Módulos

```
GeneradorPostInstagram/
├── post.py                 # Core: orquestador gráfico con Pillow y CairoSVG
├── stock.py                # Módulo: cliente de Openverse/Wikimedia con auto-scrim
├── excalidraw_engine.py    # Módulo: renderizado vectorial SVG/PNG de Excalidraw
├── brand_logo.py           # Módulo: gestión de logos vectoriales y extracción de paleta
├── anti_slop.py            # Módulo: linter de copy, detector de clichés y contraste WCAG
├── config.yaml             # Configuración principal declarativa
├── requirements.txt        # Dependencias (pillow, pyyaml, requests, cairosvg)
├── generate.sh             # Script de orquestación Unix/Mac
├── generate.bat            # Script de orquestación Windows
├── templates/              # Plantillas JSON de referencia
│   ├── default.json        # Layout card clásico con glassmorphism
│   ├── diagram.json        # Layout blueprint técnico para Excalidraw
│   ├── minimal.json        # Layout editorial suizo minimalista (4:5)
│   ├── split.json          # Layout split hero visual + contenido
│   └── quote.json          # Layout de cita o insight de alto impacto
├── custom/                 # GITIGNORED — Espacio de trabajo del usuario y del agente
│   ├── context.md          # Contexto y objetivos del proyecto
│   ├── logo.svg / logo.png # Logo de marca del usuario
│   ├── diagram.svg / .png  # Diagramas técnicos exportados de Excalidraw
│   ├── stock_cache/        # Imágenes de bancos libres descargadas y procesadas
│   ├── config.local.yaml   # Overrides que el agente o usuario aplican
│   └── config.generated.yaml# Configuración generada automáticamente
└── output/                 # GITIGNORED — Posts PNG generados (1080×1080 o 1080×1350)
```

---

## 🛡️ Habilidad Anti-IA Slop (Reglas Obligatorias)

Todo contenido generado por un agente debe pasar el filtro de calidad **Anti-IA Slop**.

### 1. Lista Negra de Clichés (Prohibidos en Copy)
**NO uses jamás:**
- ❌ *"revoluciona" / "revolucionario"*
- ❌ *"en el vertiginoso mundo de hoy"*
- ❌ *"en la era digital"*
- ❌ *"desbloquea todo el potencial"*
- ❌ *"un mundo de posibilidades"*
- ❌ *"sin precedentes"*
- ❌ *"el poder de"*
- ❌ *"a la vanguardia" / "de vanguardia"*
- ❌ *"sumérgete en"*
- ❌ *"game-changer" / "juego-cambiador"*
- ❌ *"delve", "tapestry", "testament", "unleash", "elevate", "seamlessly"*

### 2. Principios de Redacción Honesta
- **Especificidad:** Menciona hechos, cifras reales, herramientas y flujos concretos.
- **Verbos de acción directa:** En lugar de *"Descubre cómo potenciar tus clases"*, escribe *"Plantillas directas de evaluación para secundaria"*.
- **Moderación con emojis:** Máximo 1 emoji contextual por feature. Nunca uses emojis como balas decorativas genéricas.
- **Verificación:** Ejecuta siempre `python3 anti_slop.py config.yaml` para comprobar el score (debe ser 100/100).

### 3. Principios de Diseño Anti-Slop
- Evita gradientes noventeros tipo arcoíris o bolas de plástico 3D.
- Usa jerarquía tipográfica limpia (titular dominante, subtítulo con interlineado generoso, cajas con paddings de mínimo 30-40px).
- Respeta ratios de contraste mínimos WCAG AA/AAA (texto blanco sobre fondos de luminancia < 0.18 o texto oscuro sobre fondos > 0.75).

---

## 📸 Habilidad de Bancos de Imágenes Libres (`stock.py`)

El proyecto se integra directamente con la API abierta de **Openverse** (Creative Commons y Dominio Público) y **Wikimedia Commons**. No requiere claves de API.

### Uso Programático desde YAML
```yaml
stock:
  query: "minimalist architecture concrete dark"
  overlay: "dark"    # Aplica capa scrim oscura para legibilidad del texto
  blur: 0            # Desenfoque gaussiano opcional (0 a 10)
```

### Uso Directo por el Agente vía CLI
```bash
# Buscar y descargar una imagen de fondo procesada con scrim de contraste:
python3 stock.py "modern software developer desk" --overlay dark --output custom/fondo_libre.png
```

---

## 📐 Habilidad de Diagramas Excalidraw (`excalidraw_engine.py`)

Permite insertar diagramas de arquitectura, flujos o bocetos técnicos directamente en el post.

### Formatos Soportados
- **`.svg` o `.excalidraw.svg` (Recomendado):** CairoSVG lo procesa como vector a escala 2.0x, garantizando nitidez perfecta en pantallas Retina.
- **`.png` o `.excalidraw.png`:** Se auto-recortan los márgenes vacíos y se centran con suavizado Lanczos.

### Cómo configurarlo
```yaml
layout: "diagram"             # Usa el layout blueprint técnico
diagram: "custom/diagram.svg" # Ruta al diagrama exportado
```

### Previsualización Rápida
```bash
python3 excalidraw_engine.py custom/diagram.svg --preview custom/test_card.png
```

---

## 🏷️ Habilidad de Logos de Marca (`brand_logo.py`)

Soporta logos vectoriales SVG y raster PNG/WebP con canal alfa.

### Configuración en YAML
```yaml
logo:
  path: "custom/logo.svg"
  position: "top-right"      # top-right | top-left | bottom-right | bottom-left | center-top
  height: 55                 # Alto en px (ancho proporcional)
  badge: true                # Dibuja una pastilla de cristal esmerilado protectora
  extract_palette: true      # DERIVA AUTOMÁTICAMENTE la paleta cromática del post desde el logo
```

### Extracción de Paleta desde CLI
```bash
python3 brand_logo.py custom/logo.svg --palette
```

---

## 🎨 Layouts Disponibles

| Layout | Cuándo usarlo | Aspecto Recomendado |
|---|---|---|
| `card` | Presentación de producto, servicio o 3-4 características | `1:1` o `4:5` |
| `diagram` | Arquitecturas de software, flujos, Excalidraw, esquemas | `1:1` |
| `minimal` | Manifiestos, lemas contundentes, diseño editorial suizo | `4:5` (feed portrait) |
| `split` | Mitad visual (foto stock/diagrama) + mitad resumen | `1:1` |
| `quote` | Citas de impacto, testimonios, aprendizajes clave | `1:1` o `4:5` |

---

## 🤖 Playbook de Operación para Agentes (El Flujo Maestro)

### Escenario A: El usuario te dice cuál es su logo
*(Ejemplo: "Este es mi logo: custom/logo.svg, hazme una plantilla de marca")*

1. **Ejecuta la configuración de plantilla:**
   ```bash
   python3 brand_logo.py <ruta_del_logo> --setup-template "Nombre de la Marca"
   ```
2. **Qué ocurre:**
   - Se copia el logo a `custom/logo.svg` (o `.png`).
   - Se extrae la paleta cromática corporativa (`primary`, `primary_dark`, `accent_light`, `gradient_top`, `gradient_bottom`).
   - Se guarda la plantilla persistente en `custom/brand_template.yaml`.
   - Se renderiza una previsualización con `python3 post.py`.
3. **Responde al usuario:**
   Confirma que la plantilla está lista y que todos los posts que te pida a partir de ahora adoptarán automáticamente esta identidad.

---

### Escenario B: El usuario te pide un post sobre cualquier tema
*(Ejemplo: "Hazme un post sobre cómo desplegar con Docker usando mi diagrama de Excalidraw")*

1. **Redacta el contenido aplicando Anti-IA Slop:**
   - Titular honesto y dominante (3 a 7 palabras).
   - Subtítulo sin adornos ni hipérboles.
   - Puntos clave concretos con datos, herramientas o métricas reales.
   - CTA claro y creíble.
2. **Selecciona el layout:**
   - `diagram`: Si te da un esquema de Excalidraw (`custom/diagram.svg`).
   - `minimal`: Si pide formato feed vertical 4:5 con diseño suizo.
   - `split`: Si pide foto de stock de Openverse arriba y texto abajo.
   - `card`: Para lista estructurada de 3 o 4 puntos.
3. **Escribe el contenido en `custom/config.local.yaml`:**
   *(Nota: No necesitas redefinir colores ni logo; se heredan automáticamente de `custom/brand_template.yaml`).*
   ```yaml
   title: "Despliegues en Docker"
   tagline: "Arquitectura contenerizada paso a paso"
   layout: "diagram"
   diagram: "custom/diagram.svg"
   cta_text: "github.com/tu-repo"
   ```
4. **Verifica y Genera:**
   ```bash
   python3 anti_slop.py custom/config.local.yaml
   python3 post.py
   ```
5. **Muestra el Resultado:** Confirma al usuario la ruta `output/post.png`.
