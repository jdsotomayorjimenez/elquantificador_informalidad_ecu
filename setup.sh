#!/usr/bin/env bash
# Instalacion para Linux / macOS.
# Crea un entorno virtual .venv e instala las dependencias.
set -euo pipefail

# Detecta python3 o python
PY="$(command -v python3 || command -v python)"
if [[ -z "$PY" ]]; then
  echo "No se encontro Python. Instala Python 3.11+ y reintenta."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo ">> Creando entorno virtual .venv ..."
  "$PY" -m venv .venv
else
  echo ">> .venv ya existe, lo reutilizo."
fi

echo ">> Instalando dependencias ..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "Listo. Para activar el entorno:"
echo "    source .venv/bin/activate"
echo ""
echo "Luego ejecuta, por ejemplo:"
echo "    python run.py --fuente csv"
echo "    python run.py --fuente pdf --url \"https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Boletin_tecnico_anual_enero-diciembre_2025.pdf\""
