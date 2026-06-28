from __future__ import annotations
from pathlib import Path
import argparse
import sys

import pandas as pd

BASE = Path(__file__).resolve().parent.parent

# Valores ancla conocidos (verificados contra el PDF oficial).
VALORES_ESPERADOS = {
    "Morona Santiago": {"informalidad_2025": 87.4, "no_remunerado_2025": 42.0},
    "Galapagos":       {"informalidad_2025": 16.2, "no_remunerado_2025": 3.2},
    "Guayas":          {"informalidad_2025": 51.9, "no_remunerado_2025": 2.9},
    "Azuay":           {"informalidad_2025": 47.2, "no_remunerado_2025": 9.9},
}
N_PROVINCIAS = 24
R_2025_ESPERADO = 0.741
R_2024_ESPERADO = 0.717
TOL_VALOR = 0.05   # tolerancia en puntos porcentuales
TOL_R = 0.01       # tolerancia en el coeficiente de correlacion


class ValidacionError(Exception):
    pass


def _msg(provincia, columna, esperado, obtenido):
    return (
        "Validacion fallo:\n"
        f"  Provincia: {provincia}\n"
        f"  Columna: {columna}\n"
        f"  Esperado: {esperado}\n"
        f"  Obtenido: {obtenido}"
    )


def validar(df: pd.DataFrame) -> None:
    # 1) Numero de provincias
    if len(df) != N_PROVINCIAS:
        raise ValidacionError(
            f"Validacion fallo:\n  Se esperaban {N_PROVINCIAS} provincias, "
            f"se obtuvieron {len(df)}."
        )

    # 2) Columnas necesarias
    requeridas = {"provincia", "region_natural", "informalidad_2024",
                  "informalidad_2025", "no_remunerado_2024", "no_remunerado_2025"}
    faltan = requeridas - set(df.columns)
    if faltan:
        raise ValidacionError(f"Validacion fallo:\n  Faltan columnas: {sorted(faltan)}")

    idx = df.set_index("provincia")

    # 3) Valores ancla
    for prov, cols in VALORES_ESPERADOS.items():
        if prov not in idx.index:
            raise ValidacionError(
                f"Validacion fallo:\n  No se encontro la provincia '{prov}'."
            )
        for col, esperado in cols.items():
            obtenido = float(idx.loc[prov, col])
            if abs(obtenido - esperado) > TOL_VALOR:
                raise ValidacionError(_msg(prov, col, esperado, obtenido))

    # 4) Correlaciones
    r25 = df["informalidad_2025"].corr(df["no_remunerado_2025"])
    r24 = df["informalidad_2024"].corr(df["no_remunerado_2024"])
    if abs(r25 - R_2025_ESPERADO) > TOL_R:
        raise ValidacionError(_msg("(global)", "correlacion_2025",
                                   f"~{R_2025_ESPERADO}", round(r25, 3)))
    if abs(r24 - R_2024_ESPERADO) > TOL_R:
        raise ValidacionError(_msg("(global)", "correlacion_2024",
                                   f"~{R_2024_ESPERADO}", round(r24, 3)))

    print("[OK] Validacion superada:")
    print(f"     - {N_PROVINCIAS} provincias")
    print(f"     - valores ancla correctos (Morona Santiago, Galapagos, Guayas, Azuay)")
    print(f"     - correlacion 2025 r = {r25:.3f} (esperado ~{R_2025_ESPERADO})")
    print(f"     - correlacion 2024 r = {r24:.3f} (esperado ~{R_2024_ESPERADO})")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Valida un CSV del analisis.")
    ap.add_argument("--csv", default=str(BASE / "data" / "enemdu_anual_2025_provincial.csv"))
    args = ap.parse_args(argv)
    df = pd.read_csv(args.csv)
    try:
        validar(df)
    except ValidacionError as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
