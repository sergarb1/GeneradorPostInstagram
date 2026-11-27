@echo off
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
set MODE_FILE=custom\.mode

rem ── parse args ──────────────────────────────────────────────
if "%1"=="--modo" (
    if "%2"=="" (
        echo Uso: %0 --modo manual^|opencode^|freebuff^|antigravity^|gemini^|claude
        pause
        exit /b 1
    )
    if not exist custom mkdir custom
    echo %2 > "%MODE_FILE%"
    echo ✓ Modo cambiado a: %2
    exit /b 0
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Necesitas Python 3: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist fonts\Outfit-Bold.ttf (
    echo 📥 Descargando fuentes Outfit...
    mkdir fonts 2>nul
    python -c "
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
" 2>nul
)

rem ── dependencias ─────────────────────────────────────────────
pip install -q --break-system-packages pillow pyyaml requests cairosvg 2>nul || pip install -q pillow pyyaml requests cairosvg 2>nul

if not exist "%MODE_FILE%" (
    echo.
    echo 🎨 ¿Cómo quieres crear tu post de Instagram?
    echo.
    echo   1) Manual / Directo — renderiza post.py con argumentos CLI
    echo   2) opencode / freebuff / Claude / Gemini — Asistente de IA
    echo.
    set /p choice="Elige (1-2) [1]: "
    if "%choice%"=="" set choice=1
    if not exist custom mkdir custom
    if "%choice%"=="2" ( echo ai > "%MODE_FILE%" ) else ( echo manual > "%MODE_FILE%" )
    echo ✓ Modo guardado
)

set /p MODE=<"%MODE_FILE%"
echo 📋 Modo: %MODE%    (cambia con: --modo manual^|opencode^|freebuff^|antigravity^|gemini^|claude)

if "%MODE%"=="manual" (
    python post.py %*
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
echo Eres un director de arte y redactor publicitario de élite.
echo Tu objetivo es generar el archivo de configuración YAML para un post de Instagram de alto impacto.
echo.
echo REGLAS ESTRICTAS ANTI-IA SLOP ^(OBLIGATORIAS^):
echo 1. PROHIBIDO usar lenguaje publicitario inflado o clichés de IA:
echo    - NO uses: "revoluciona", "en el vertiginoso mundo", "en la era digital", "desbloquea el poder", "un mundo de posibilidades", "sin precedentes", "de vanguardia", "game-changer", "delve", "tapestry".
echo 2. Sé directo, conciso, humano y específico. Usa verbos enérgicos y hechos demostrables.
echo 3. Layouts disponibles: 'card', 'diagram', 'minimal', 'split', 'quote'.
echo 4. Responde UNICAMENTE con el bloque YAML válido, sin introducciones ni despedidas.
echo.
echo Contexto del proyecto:
echo ---
echo %CONTEXT%
echo ---
) > custom\prompt.md

echo.
echo ✅ Prompt Anti-IA Slop preparado en custom\prompt.md
echo.
echo Puedes pasarlo a tu asistente de IA (Freebuff, OpenCode, Claude, etc.):
echo   type custom\prompt.md ^| opencode
echo.
echo Cuando tengas el YAML, guárdalo en custom\config.generated.yaml
echo y ejecuta: python post.py
echo.
