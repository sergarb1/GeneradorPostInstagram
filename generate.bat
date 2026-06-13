@echo off
REM Generador de posts Instagram — Windows
chcp 65001 >nul

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM ── check deps ────────────────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Necesitas Python 3. Instalalo desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM ── descargar fuentes ─────────────────────────────────────
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

REM ── instalar deps ─────────────────────────────────────────
echo 📦 Instalando dependencias...
pip install -q pillow pyyaml requests

REM ── generar post ──────────────────────────────────────────
echo 🖼  Generando post...
python post.py

echo.
pause
