@echo off
REM Instalacion para Windows (CMD).
REM Crea un entorno virtual .venv e instala las dependencias.

where python >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python. Instala Python 3.11+ y marca "Add to PATH".
  exit /b 1
)

if not exist ".venv" (
  echo ^>^> Creando entorno virtual .venv ...
  python -m venv .venv
) else (
  echo ^>^> .venv ya existe, lo reutilizo.
)

echo ^>^> Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Listo. Para activar el entorno en CMD:
echo     .venv\Scripts\activate.bat
echo Para activar en PowerShell:
echo     .venv\Scripts\Activate.ps1
echo.
echo Luego ejecuta, por ejemplo:
echo     python run.py --fuente csv
echo     python run.py --fuente pdf --url "https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Boletin_tecnico_anual_enero-diciembre_2025.pdf"
