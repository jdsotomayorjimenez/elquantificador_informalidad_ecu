#!/usr/bin/env bash
# Atajo para Linux / macOS. La logica real esta en run.py (multiplataforma).
#
#   bash run.sh                       -> ruta rapida (CSV de referencia)
#   bash run.sh PDF /ruta/boletin.pdf -> ruta fuerte desde PDF local
#   bash run.sh URL https://...       -> ruta fuerte descargando el PDF
set -euo pipefail

PY="./.venv/bin/python"
[[ -x "$PY" ]] || PY="$(command -v python3 || command -v python)"

case "${1:-}" in
  PDF) "$PY" run.py --fuente pdf --pdf "${2:?Falta la ruta del PDF}" ;;
  URL) "$PY" run.py --fuente pdf --url "${2:?Falta la URL del PDF}" ;;
  *)   "$PY" run.py --fuente csv ;;
esac
