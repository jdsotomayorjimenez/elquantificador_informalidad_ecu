# Instalacion para Windows (PowerShell).
# Crea un entorno virtual .venv e instala las dependencias.
# Si PowerShell bloquea el script, ejecuta antes:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$ErrorActionPreference = "Stop"

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "No se encontro Python. Instala Python 3.11+ y marca 'Add to PATH'."
    exit 1
}

if (-not (Test-Path ".venv")) {
    Write-Host ">> Creando entorno virtual .venv ..."
    python -m venv .venv
} else {
    Write-Host ">> .venv ya existe, lo reutilizo."
}

Write-Host ">> Instalando dependencias ..."
& ".venv\Scripts\python.exe" -m pip install --upgrade pip
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host ""
Write-Host "Listo. Para activar el entorno en PowerShell:"
Write-Host "    .venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Luego ejecuta, por ejemplo:"
Write-Host "    python run.py --fuente csv"
