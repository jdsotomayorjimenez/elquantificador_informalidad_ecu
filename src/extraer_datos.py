from __future__ import annotations
import argparse
import io
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
CSV_SALIDA = BASE / "data" / "enemdu_desde_pdf.csv"
DEBUG_TXT = BASE / "output" / "debug" / "texto_extraido_pdf.txt"

# Invariante del parser: las Tablas 8 y 9 van seguidas, asi que la PRIMERA aparicion
# de cada provincia (con dos %) es no remunerado (T8) y la SEGUNDA es informalidad (T9).
# Se ancla a la ULTIMA ocurrencia de este titulo para saltar el indice.
ANCLA_TABLA_8 = "empleo no remunerado a nivel provincial"

PROVINCIAS = [
    "Azuay", "Bolivar", "Cañar", "Carchi", "Cotopaxi", "Chimborazo", "El Oro",
    "Esmeraldas", "Guayas", "Imbabura", "Loja", "Los Rios", "Manabi",
    "Morona Santiago", "Napo", "Pastaza", "Pichincha", "Tungurahua",
    "Zamora Chinchipe", "Galapagos", "Sucumbios", "Orellana", "Santo Domingo",
    "Santa Elena",
]

REGION = {
    "Azuay": "Sierra", "Bolivar": "Sierra", "Cañar": "Sierra", "Carchi": "Sierra",
    "Cotopaxi": "Sierra", "Chimborazo": "Sierra", "Imbabura": "Sierra",
    "Loja": "Sierra", "Pichincha": "Sierra", "Tungurahua": "Sierra",
    "El Oro": "Costa", "Esmeraldas": "Costa", "Guayas": "Costa", "Los Rios": "Costa",
    "Manabi": "Costa", "Santo Domingo": "Costa", "Santa Elena": "Costa",
    "Morona Santiago": "Amazonia", "Napo": "Amazonia", "Pastaza": "Amazonia",
    "Zamora Chinchipe": "Amazonia", "Sucumbios": "Amazonia", "Orellana": "Amazonia",
    "Galapagos": "Insular",
}

# Multipalabra y largos primero para que "Morona Santiago" gane sobre fragmentos cortos.
_NOMBRES_PATRON = [
    r"Morona\s+Santiago", r"Zamora\s+Chinchipe", r"Santo\s+Domingo",
    r"Santa\s+Elena", r"Los\s+R[íi]os", r"El\s+Oro",
    r"Chimborazo", r"Esmeraldas", r"Imbabura", r"Tungurahua", r"Sucumb[íi]os",
    r"Gal[áa]pagos", r"Cotopaxi", r"Pichincha", r"Orellana", r"Pastaza",
    r"Bol[íi]var", r"Manab[íi]", r"Carchi", r"Guayas", r"Azuay", r"Ca[ñn]ar",
    r"Loja", r"Napo",
]
_RE_FILA = re.compile(
    r"\b(" + "|".join(_NOMBRES_PATRON) + r")\s+(\d{1,3},\d+)\s*%\s+(\d{1,3},\d+)\s*%"
)


def _canon(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower().strip()


_LOOKUP = {_canon(p): p for p in PROVINCIAS}


def obtener_texto(pdf=None, url=None, guardar_debug=True) -> str:
    import pdfplumber

    if pdf:
        origen = str(pdf)
    elif url:
        with urllib.request.urlopen(url) as r:
            origen = io.BytesIO(r.read())
    else:
        raise ValueError("Debes indicar --pdf o --url")

    partes = []
    with pdfplumber.open(origen) as doc:
        for pagina in doc.pages:
            partes.append(pagina.extract_text() or "")
    texto = "\n".join(partes)

    if guardar_debug:
        DEBUG_TXT.parent.mkdir(parents=True, exist_ok=True)
        DEBUG_TXT.write_text(texto, encoding="utf-8")
        print(f"Texto del PDF guardado en: {DEBUG_TXT}")
    return texto


def _extraer_pares(texto: str):
    inicio = texto.lower().rfind(ANCLA_TABLA_8.lower())
    if inicio == -1:
        raise ValueError(
            "No se encontro el titulo de la Tabla 8 en el PDF. "
            "Revisa output/debug/texto_extraido_pdf.txt para ver que se leyo."
        )
    region = texto[inicio:]

    t8: dict[str, tuple[float, float]] = {}
    t9: dict[str, tuple[float, float]] = {}
    for m in _RE_FILA.finditer(region):
        prov = _LOOKUP.get(_canon(m.group(1)))
        if prov is None:
            continue
        par = (float(m.group(2).replace(",", ".")), float(m.group(3).replace(",", ".")))
        if prov not in t8:
            t8[prov] = par        # 1a aparicion -> Tabla 8 (no remunerado)
        elif prov not in t9:
            t9[prov] = par        # 2a aparicion -> Tabla 9 (informalidad)
    return t8, t9


def construir_dataframe(texto: str) -> pd.DataFrame:
    t8, t9 = _extraer_pares(texto)
    faltan8 = [p for p in PROVINCIAS if p not in t8]
    faltan9 = [p for p in PROVINCIAS if p not in t9]
    if faltan8 or faltan9:
        raise ValueError(
            "Extraccion incompleta.\n"
            f"  Faltan en Tabla 8 (no remunerado): {faltan8}\n"
            f"  Faltan en Tabla 9 (informalidad):  {faltan9}\n"
            "  Revisa output/debug/texto_extraido_pdf.txt para ver el texto leido."
        )
    filas = [{
        "provincia": p,
        "region_natural": REGION[p],
        "informalidad_2024": t9[p][0],
        "informalidad_2025": t9[p][1],
        "no_remunerado_2024": t8[p][0],
        "no_remunerado_2025": t8[p][1],
    } for p in PROVINCIAS]
    return pd.DataFrame(filas)


def extraer(pdf=None, url=None, salida=CSV_SALIDA) -> pd.DataFrame:
    texto = obtener_texto(pdf=pdf, url=url)
    df = construir_dataframe(texto)
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False)
    print(f"Extraidas {len(df)} provincias del PDF -> {salida}")
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extrae datos del PDF ENEMDU anual 2025.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pdf", help="Ruta local del PDF del boletin")
    g.add_argument("--url", help="URL del PDF del boletin")
    ap.add_argument("--salida", default=str(CSV_SALIDA))
    args = ap.parse_args(argv)
    try:
        extraer(pdf=args.pdf, url=args.url, salida=args.salida)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR durante la extraccion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
