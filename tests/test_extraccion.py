"""
Prueba el parser de extraccion contra el texto real del PDF (fixture) y verifica
que reproduce exactamente el CSV de referencia, ademas de pasar las validaciones
obligatorias.

Uso:
    python tests/test_extraccion.py
"""
from pathlib import Path
import sys

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from extraer_datos import construir_dataframe, PROVINCIAS  # noqa: E402
from validar_datos import validar  # noqa: E402

FIXTURE = BASE / "tests" / "fixture_texto_pdf.txt"
REF = BASE / "data" / "enemdu_anual_2025_provincial.csv"


def main():
    texto = FIXTURE.read_text(encoding="utf-8")
    extraido = construir_dataframe(texto).sort_values("provincia").reset_index(drop=True)
    ref = pd.read_csv(REF).sort_values("provincia").reset_index(drop=True)

    cols = ["informalidad_2024", "informalidad_2025",
            "no_remunerado_2024", "no_remunerado_2025"]

    assert len(extraido) == len(PROVINCIAS) == 24, "No se extrajeron 24 provincias"
    assert list(extraido["provincia"]) == list(ref["provincia"]), "Provincias no coinciden"

    ok = True
    for c in cols:
        difer = ref[~(ref[c] == extraido[c])]
        if len(difer):
            ok = False
            print(f"[FALLA] columna {c}: diferencias en {list(difer['provincia'])}")
    if not ok:
        sys.exit("El parser NO reproduce el CSV de referencia.")

    print("[OK] El parser reproduce exactamente las 24 provincias x 4 columnas")
    print("[OK] Extraccion desde texto-PDF == CSV de referencia")

    # Validaciones obligatorias sobre lo extraido
    validar(extraido)


if __name__ == "__main__":
    main()
