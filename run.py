from __future__ import annotations
import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "src"))

import pandas as pd  # noqa: E402
from validar_datos import validar, ValidacionError  # noqa: E402
from grafico import generar_grafico  # noqa: E402

CSV_REF = BASE / "data" / "enemdu_anual_2025_provincial.csv"
CSV_PDF = BASE / "data" / "enemdu_desde_pdf.csv"


def _paso(n, total, texto):
    print(f"\n>> {n}/{total}  {texto}")


def flujo_pdf(pdf=None, url=None):
    from extraer_datos import extraer

    total = 3
    _paso(1, total, "Extrayendo Tablas 8 y 9 desde el PDF oficial...")
    df = extraer(pdf=pdf, url=url, salida=CSV_PDF)

    _paso(2, total, "Validando las cifras extraidas...")
    validar(df)

    _paso(3, total, "Generando la figura desde el CSV extraido del PDF...")
    generar_grafico(CSV_PDF)


def flujo_csv(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        sys.exit(f"ERROR: no existe el CSV: {csv_path}")
    total = 2
    _paso(1, total, f"Validando el CSV: {csv_path.name} ...")
    df = pd.read_csv(csv_path)
    validar(df)

    _paso(2, total, "Generando la figura...")
    generar_grafico(csv_path)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Flujo reproducible PDF/CSV -> validacion -> grafico.")
    ap.add_argument("--fuente", choices=["csv", "pdf"], default="csv",
                    help="Origen de los datos (por defecto: csv)")
    ap.add_argument("--pdf", help="Ruta local del PDF (con --fuente pdf)")
    ap.add_argument("--url", help="URL del PDF (con --fuente pdf)")
    ap.add_argument("--csv", help="Ruta del CSV (con --fuente csv). "
                                  "Por defecto, el CSV de referencia verificado.")
    args = ap.parse_args(argv)

    try:
        if args.fuente == "pdf":
            if not args.pdf and not args.url:
                sys.exit("ERROR: con --fuente pdf debes indicar --pdf RUTA o --url URL")
            flujo_pdf(pdf=args.pdf, url=args.url)
        else:
            flujo_csv(args.csv or CSV_REF)
    except ValidacionError as e:
        print("\n" + str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nListo. Revisa output/informalidad_ecuador.png")


if __name__ == "__main__":
    main()
