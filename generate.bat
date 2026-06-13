@echo off
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
set MODE_FILE=custom\.mode

rem ── parse args ──────────────────────────────────────────────
if "%1"=="--modo" (
    if "%2"=="" (
        echo Uso: %0 --modo manual^|opencode^|gemini^|codex^|claude
        pause
        exit /b 1
    )
    if not exist custom mkdir custom
    echo %2 > "%MODE_FILE%"
    echo ✓ Modo cambiado a: %2
    pause
    exit /b 0
)
if "%1"=="-m" (
    if "%2"=="" (
        echo Uso: %0 --modo manual^|opencode^|gemini^|codex^|claude
        pause
        exit /b 1
    )
    if not exist custom mkdir custom
    echo %2 > "%MODE_FILE%"
    echo ✓ Modo cambiado a: %2
    pause
    exit /b 0
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Necesitas Python 3: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist fonts\* (
    echo 📥 Descargando fuentes...
    mkdir fonts 2>nul
    python -c "
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
"
)

echo 📦 Instalando dependencias...
pip install -q --break-system-packages pillow pyyaml requests

if not exist "%MODE_FILE%" (
    echo.
    echo 🎨 ¿Cómo quieres crear tu post de Instagram?
    echo.
    echo   1) Manual — te guío paso a paso con preguntas
    echo   2) IA — prepara un prompt interactivo para ChatGPT, Claude, etc.
    echo.
    set /p choice="Elige (1-2) [1]: "
    if "%choice%"=="" set choice=1
    if "%choice%"=="2" ( echo ai > "%MODE_FILE%" ) else ( echo manual > "%MODE_FILE%" )
    echo ✓ Modo guardado
)

set /p MODE=<"%MODE_FILE%"
echo 📋 Modo: %MODE%    (cambia con: --modo manual^|opencode^|gemini^|codex^|claude)

if "%MODE%"=="manual" (
    python post.py --interactive
    pause
    exit /b 0
)

rem ── modo IA ──────────────────────────────────────────────────
if not exist custom\context.md (
    echo.
    echo 📝 Describe tu proyecto:
    set /p context="> "
    if not exist custom mkdir custom
    echo %context% > custom\context.md
    echo ✓ Guardado
)

set /p CONTEXT=<custom\context.md

if not exist custom mkdir custom
(
echo Eres un asistente experto en marketing educativo.
echo.
echo Entrevista al usuario para crear un post de Instagram.
echo Pregunta una cosa a la vez. Cuando tengas toda la informacion,
echo responde UNICAMENTE con el YAML, sin explicaciones.
echo.
echo El YAML debe tener:
echo - title: titulo llamativo (max 40 caracteres)
echo - tagline: frase corta (max 60)
echo - body: texto con \n para saltos (max 200)
echo - features: 4 items con icon (emoji), title, desc
echo - cta_text: texto del boton
echo - hashtags: separados por espacios
echo.
echo Contexto del proyecto:
echo ---
echo %CONTEXT%
echo ---
echo.
echo Empieza la conversacion. Saluda al usuario.
) > custom\prompt.md

echo.
echo ✅ Prompt preparado en custom\prompt.md
echo.
echo Puedes copiarlo a ChatGPT, Claude, etc. o ejecutar:
echo   type custom\prompt.md ^| opencode
echo.
echo Cuando tengas el YAML, guardalo en custom\config.generated.yaml
echo y ejecuta: python post.py
echo.
pause
