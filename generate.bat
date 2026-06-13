@echo off
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
set MODE_FILE=custom\.mode

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
    with open(f'fonts/{name}', 'wb') as f:
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
    echo   2) IA — prepara un prompt para ChatGPT, Claude, etc.
    echo.
    set /p choice="Elige (1-2) [1]: "
    if "%choice%"=="" set choice=1
    if "%choice%"=="2" ( echo ai > "%MODE_FILE%" ) else ( echo manual > "%MODE_FILE%" )
    echo ✓ Modo guardado
)

set /p MODE=<"%MODE_FILE%"
echo 📋 Modo: %MODE%

if "%MODE%"=="manual" (
    python post.py --interactive
    pause
    exit /b 0
)

rem ── modo IA ──────────────────────────────────────────────────
if not exist custom\context.md (
    echo.
    echo 📝 Describe tu proyecto:
    echo.
    set /p context="> "
    if not exist custom mkdir custom
    echo %context% > custom\context.md
    echo ✓ Guardado
)

set /p CONTEXT=<custom\context.md

if not exist custom mkdir custom
(
echo Eres un experto en marketing educativo. Crea un archivo YAML para un post de Instagram promocional.
echo.
echo El YAML debe tener estas claves:
echo - title: titulo llamativo (max 40 caracteres)
echo - tagline: frase corta (max 60)
echo - body: texto con \n para saltos (max 200)
echo - features: 4 items con icon (emoji), title, desc
echo - cta_text: texto del boton
echo - hashtags: separados por espacios
echo.
echo Contexto:
echo ---
echo %CONTEXT%
echo ---
echo YAML:
) > custom\prompt.md

echo.
echo ✅ Prompt listo en custom\prompt.md
echo.
echo Pásalo a tu IA favorita y guarda el resultado en custom\config.generated.yaml
echo Luego ejecuta: python post.py
echo.
pause
