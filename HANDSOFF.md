# GeneradorPostInstagram 2.0 — Manual de Traspaso y Operaciones (HANDSOFF.md)

Este documento es la **guía operativa completa** para creadores de contenido, equipos de marketing, desarrolladores y administradores de sistemas que utilizan o mantienen **GeneradorPostInstagram 2.0**.

---

## 1. 📖 Resumen Ejecutivo y Filosofía del Sistema

### ¿Por qué este generador NO es un programa interactivo monolítico?
Muchos generadores gráficos intentan crear asistentes interactivos en terminal (*wizards* con 20 preguntas) o interfaces gráficas pesadas que se vuelven lentas, frágiles y complejas de mantener. 

**GeneradorPostInstagram 2.0 adopta la filosofía Agent-First:**
- **El motor es 100% declarativo y modular:** Toma un archivo YAML con especificaciones claras y produce un PNG de alta definición (1080×1080 o 1080×1350) en menos de 1 segundo.
- **La creatividad la lidera un asistente de IA (Antigravity, OpenCode, Freebuff, Claude o Gemini):** Tú le hablas al asistente en lenguaje natural, y el asistente manipula el YAML, busca fotos en bancos libres, encuadra diagramas de Excalidraw y verifica el contenido contra clichés de IA.
- **Cero dependencias innecesarias de servidor:** Funciona localmente, sin cuentas de pago, sin suscripciones a APIs cerradas y con licencias de código abierto (AGPL v3).

---

## 2. 🏛️ Arquitectura del Pipeline

El sistema se compone de 5 piezas desacopladas:

```
                  ┌──────────────────────────────────────────────┐
                  │    Asistente de IA / Creador Humano          │
                  │   (Antigravity, OpenCode, Freebuff, etc.)    │
                  └──────────────────────┬───────────────────────┘
                                         │ Configura
                                         ▼
                                 ┌──────────────┐
                                 │ config.yaml  │
                                 └───────┬──────┘
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   ▼                     ▼                     ▼
        ┌────────────────────┐ ┌───────────────────┐ ┌───────────────────┐
        │     stock.py       │ │  excalidraw_      │ │   brand_logo.py   │
        │                    │ │    engine.py      │ │                   │
        │ • Openverse API    │ │ • CairoSVG (Retina│ │ • SVG / PNG Alpha │
        │ • Wikimedia Commons│ │ • Smart Crop Trim │ │ • Frosted Badge   │
        │ • Auto-scrim Dark  │ │ • Blueprint Frame │ │ • Auto-Palette    │
        └──────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         ▼
                                 ┌──────────────┐
                                 │ anti_slop.py │ (Linter de honestidad y copy)
                                 └───────┬──────┘
                                         ▼
                                 ┌──────────────┐
                                 │   post.py    │ (Composición Pillow)
                                 └───────┬──────┘
                                         ▼
                                 ┌──────────────┐
                                 │  output/     │ (PNG 1080×1080 / 1080×1350)
                                 │   post.png   │
                                 └──────────────┘
```

---

## 3. 💻 Instalación y Requisitos del Sistema

### Requisitos Básicos
- **Python 3.9 o superior**
- **Cairo 2D Library** (para renderizado vectorial de SVG)

### Linux (Debian / Ubuntu / Mint)
```bash
# 1. Instalar Cairo y Python
sudo apt update
sudo apt install -y python3 python3-pip libcairo2 libcairo2-dev

# 2. Instalar dependencias Python
pip install --break-system-packages -r requirements.txt
# o sin --break-system-packages si usas un entorno virtual
```

### macOS
```bash
# Con Homebrew
brew install cairo python3
pip3 install -r requirements.txt
```

### Windows
```cmd
pip install -r requirements.txt
```
*(En Windows, si no tienes Cairo nativo, `cairosvg` incluye precompilados o el generador utiliza automáticamente PNGs transparentes).*

---

## 4. 🚀 Modos de Uso y Flujos de Trabajo

### Flujo A: Trabajando con tu Asistente de IA (OpenCode / Freebuff / Antigravity)

Este es el flujo principal para el que está diseñado el proyecto:

#### 1. Crear tu Plantilla de Marca (Una sola vez)
Abres tu asistente (por ejemplo, `opencode`) en esta carpeta y le dices:
> *"Este es mi logo: custom/logo.svg, créame una plantilla de marca."*

El asistente ejecuta internamente `python3 brand_logo.py <logo> --setup-template "Tu Marca"`, lo que:
- Extrae la paleta cromática de tu logo (primario, oscuro, acento pastel y degradados).
- Genera la plantilla persistente en `custom/brand_template.yaml`.
- Configura el logo con su pastilla protectora de cristal esmerilado (*frosted glass pill*).
- Genera una previsualización de tu marca en `output/post.png`.

#### 2. Generar Posts Continuos a partir de la Plantilla
A partir de ahí, solo le dices al asistente de qué quieres hablar:
> *"Hazme un post sobre cómo desplegar con Docker usando mi diagrama de Excalidraw custom/diagram.svg"*  
> *"Hazme un post con fondo de Openverse sobre educación alternativa en layout minimal"*

El asistente:
1. Aplica las **reglas estrictas Anti-IA Slop** (sin clichés como *"revoluciona"* o *"desbloquea"*).
2. Escribe únicamente el nuevo contenido en `custom/config.local.yaml`.
3. El motor **hereda automáticamente tu plantilla de marca** (`custom/brand_template.yaml`), manteniendo tus colores corporativos, tipografía y logo sin tener que reconfigurarlos cada vez.
4. Ejecuta `python3 post.py` y te entrega el post listo en `output/post.png`.

### Flujo B: Ejecución Rápida por Terminal (CLI)
Puedes sobreescribir cualquier parámetro desde la línea de comandos sin tocar el archivo YAML:

```bash
# 1. Post básico con configuración actual:
./generate.sh

# 2. Buscar foto de fondo en Openverse y aplicar layout split:
./generate.sh --stock "cyberpunk minimal city" --layout split

# 3. Post de arquitectura técnica con diagrama de Excalidraw:
./generate.sh --diagram custom/mi_diagrama.svg --layout diagram

# 4. Formato vertical de feed de Instagram (1080×1350) en estilo suizo:
./generate.sh --layout minimal --aspect 4:5

# 5. Comprobar que no hay clichés de IA en el texto:
./generate.sh --anti-slop
```

### Flujo C: Edición Manual del YAML
Edita `config.yaml` directamente con tu editor preferido (VS Code, Nano, Cursor) y ejecuta:
```bash
python3 post.py
```

---

## 5. 📐 Guía de Excalidraw para Diagramas de Arquitectura

Excalidraw es la herramienta estándar para bocetos técnicos, arquitecturas cloud y flujos de software.

### Cómo exportar desde Excalidraw:
1. Abre tu diagrama en [excalidraw.com](https://excalidraw.com).
2. Ve al menú superior izquierdo → **Exportar imagen** (o pulsa `Ctrl + Shift + E`).
3. Formato recomendado: **SVG** (vectorial nítido a cualquier resolución).
4. Activa la casilla **Fondo transparente** si deseas que tome el tema del post, o mantén fondo blanco.
5. Guarda el archivo en la carpeta `custom/diagram.svg`.
6. En tu `config.yaml` especifica:
   ```yaml
   layout: "diagram"
   diagram: "custom/diagram.svg"
   ```
7. Ejecuta `python3 post.py` y obtendrás el diagrama perfectamente encuadrado dentro de una tarjeta con aspecto de blueprint técnico.

---

## 6. 📸 Guía de Bancos de Imágenes Libres (Openverse / Wikimedia)

El generador incluye integración nativa con la API de **Openverse** (el índice de Creative Commons de WordPress Foundation) con más de 700 millones de imágenes libres.

### Cómo funciona el Auto-Scrim:
Al poner texto sobre fotos reales, el mayor error de diseño es la pérdida de contraste. Nuestro módulo `stock.py`:
1. Descarga la imagen en alta resolución.
2. Realiza un **recorte inteligente centrado** al aspecto exacto (1:1 o 4:5).
3. Aplica una capa degradada translúcida (*scrim* vertical oscuro) de luminancia controlada.
4. Permite aplicar un desenfoque gaussiano suave opcional (`blur: 3`) para dar profundidad de campo.

### Configuración en YAML:
```yaml
stock:
  query: "nature minimal fog mountain"  # Búsqueda en lenguaje natural
  overlay: "dark"                       # dark | light | vignette | none
  blur: 0                               # 0 = nítido, 1 a 10 = desenfoque
```

---

## 7. 🏷️ Identidad de Marca y Logos

El módulo `brand_logo.py` cuida la presencia de marca sin invadir el post:

### Opciones de Logo en YAML:
```yaml
logo:
  path: "custom/logo.svg"       # Admite .svg, .png o .webp
  position: "top-right"         # top-right | top-left | bottom-right | bottom-left | center-top
  height: 55                    # Altura en píxeles (ancho automático)
  badge: true                   # Pastilla de cristal esmerilado detrás del logo
  extract_palette: true         # Deriva automáticamente la paleta del post desde el logo
```

### Extracción de Paleta Automática:
Si activas `extract_palette: true`, el motor cuantiza los colores del logo y deriva matemáticamente:
- `primary`: Color principal vibrante.
- `primary_dark`: Tono oscuro profundo contrastado para textos.
- `gradient_top` / `gradient_bottom`: Fondo armonizado con la identidad corporativa.
- `accent_light`: Color complementario claro para badges y píldoras.

---

## 8. 🛡️ Guía Anti-IA Slop (Control de Calidad)

El término **AI Slop** define el contenido insulso, inflado y genérico generado por modelos de lenguaje cuando no se les instruye con rigor.

### Las 3 Reglas de Oro de Redacción:
1. **Sin Hipérboles:** No digas que una herramienta *"revoluciona el futuro"*; di *"ahorra 2 horas en la creación de exámenes"*.
2. **Especificidad:** Emplea sustantivos concretos y datos verificables.
3. **Economía de palabras:** Si una frase no aporta información nueva, elimínala.

### Ejecutar el Linter:
```bash
python3 anti_slop.py config.yaml
```
Si detecta palabras como *"revoluciona"*, *"delve"* o más de 4 emojis por post, mostrará advertencias y consejos de redacción específicos.

---

## 9. 🎨 Catálogo de Layouts

- **`card`**: El layout todoterreno. Tarjeta flotante con efecto glassmorphism, titulares limpios y 4 características con iconos o números ordinales elegantes (`01`, `02`).
- **`diagram`**: Especializado para ingenieros, desarrolladores y arquitectos. Coloca un visor de diagrama central con marco técnico y barra inferior de conclusiones.
- **`minimal`**: Inspirado en la escuela suiza de diseño gráfico. Titular gigante, generoso espacio negativo, línea de acento sutil y máxima sofisticación.
- **`split`**: Mitad superior para fotografía de stock o diagrama, mitad inferior para tarjeta descriptiva.
- **`quote`**: Comillas tipográficas gigantes para citas destacadas, lemas institucionales o reflexiones de líderes de opinión.

---

## 10. 🔧 Preguntas Frecuentes y Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'cairosvg'`
- Asegúrate de haber instalado Cairo en el sistema (`sudo apt install libcairo2` en Linux o `brew install cairo` en Mac).
- Si usas Python con `--break-system-packages`, el generador detecta automáticamente paquetes en `~/.local/lib/python3.*/site-packages`.

### Las fuentes se ven genéricas
- El script descarga automáticamente `Outfit-Bold.ttf` y `Outfit-Regular.ttf` a la carpeta `fonts/`. Si no tienes conexión a internet, se usan las fuentes estándar del sistema (`DejaVuSans-Bold.ttf`).

### ¿Dónde se guardan los archivos generados?
- Siempre en `output/post.png`. Esta carpeta está en `.gitignore` para no ensuciar el repositorio de Git.

---

## 11. 📦 Mantenimiento y Extensiones

- **Añadir un nuevo layout:** Agrega la función `render_nombrelayout(...)` en `post.py` y regístrala en la función `generate_post()`.
- **Añadir nuevas fuentes:** Coloca cualquier archivo `.ttf` en la carpeta `fonts/` y referéncialo en `config.yaml` bajo la sección `fonts:`.
- **Integración con GitHub Actions / CI:** Se puede configurar un workflow de GitHub Actions que ejecute `python3 post.py` ante cualquier cambio en `config.yaml` y publique el post automáticamente o lo guarde como artefacto.
