@echo off
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

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

echo 🖼  Generando post...
python post.py --interactive

echo.
pause
