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

rem ── elegir modo ──────────────────────────────────────────────
if not exist "%MODE_FILE%" (
    echo.
    echo 🎨 ¿Cómo quieres crear tu post de Instagram?
    echo.
    echo   1) Manual — te guío paso a paso con preguntas
    echo   2) opencode — IA local
    echo   3) Gemini CLI — IA de Google
    echo   4) Codex CLI — IA de OpenAI
    echo   5) Claude CLI — IA de Anthropic
    echo.
    set /p choice="Elige (1-5) [1]: "
    if "%choice%"=="" set choice=1
    if "%choice%"=="1" set MODE=manual
    if "%choice%"=="2" set MODE=opencode
    if "%choice%"=="3" set MODE=gemini
    if "%choice%"=="4" set MODE=codex
    if "%choice%"=="5" set MODE=claude
    if "%MODE%"=="" set MODE=manual
    if not exist custom mkdir custom
    echo %MODE% > "%MODE_FILE%"
    echo ✓ Modo guardado
) else (
    set /p MODE=<"%MODE_FILE%"
)
echo 📋 Modo: %MODE%

if "%MODE%"=="manual" (
    python post.py --interactive
    pause
    exit /b 0
)

echo 🤖 Modo IA no disponible en Windows. Usando modo manual.
python post.py --interactive
pause
