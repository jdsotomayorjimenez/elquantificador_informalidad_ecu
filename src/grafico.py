from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
CSV_REF = BASE / "data" / "enemdu_anual_2025_provincial.csv"
OUT = BASE / "output"

PROMEDIO_NACIONAL = 51.5  # tasa nacional ponderada de informalidad 2025 (INEC)
ANOTAR = [
    "Morona Santiago", "Napo", "Orellana",
    "Bolivar",
    "Guayas", "Santa Elena",
    "Azuay",
    "Pichincha", "Galapagos",
]
COLORES = {
    "Costa": "#2C7FB8", "Sierra": "#D95F0E",
    "Amazonia": "#31A354", "Insular": "#7B6FB0",
}


def generar_grafico(csv_path=CSV_REF, out_dir=OUT):
    csv_path = Path(csv_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    r = df["informalidad_2025"].corr(df["no_remunerado_2025"])

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.edgecolor": "#cccccc", "axes.linewidth": 0.8,
        "figure.facecolor": "#FBFAF7", "axes.facecolor": "#FBFAF7",
    })

    fig = plt.figure(figsize=(14, 8.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.75, 1], wspace=0.28,
                          left=0.06, right=0.975, top=0.80, bottom=0.10)
    ax = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])

    # --- Panel principal: scatter ---
    m, b = np.polyfit(df["informalidad_2025"], df["no_remunerado_2025"], 1)
    xs = np.array([df["informalidad_2025"].min(), df["informalidad_2025"].max()])
    ax.plot(xs, m * xs + b, color="#999999", lw=1, ls="--", zorder=1)
    ax.set_ylim(-1, 46)
    ax.set_xlim(10, 95)

    for region, sub in df.groupby("region_natural"):
        ax.scatter(sub["informalidad_2025"], sub["no_remunerado_2025"],
                   s=70, color=COLORES.get(region, "#888888"), label=region,
                   edgecolor="white", linewidth=0.8, zorder=3)

    ax.axvline(PROMEDIO_NACIONAL, color="#666666", lw=0.9, ls=":", zorder=2)
    ax.text(PROMEDIO_NACIONAL + 0.6, ax.get_ylim()[1] * 0.97,
            f"Tasa nacional\n{PROMEDIO_NACIONAL}%", fontsize=8.5,
            color="#666666", va="top", ha="left")

    offsets = {
        "Morona Santiago": (-8, 4), "Napo": (8, -2), "Orellana": (-10, -16),
        "Bolivar": (8, 2), "Guayas": (8, -4), "Santa Elena": (8, 2),
        "Azuay": (-8, 6), "Pichincha": (8, 4), "Galapagos": (8, 2),
    }
    ha_map = {"Morona Santiago": "right", "Orellana": "right", "Azuay": "right"}
    for _, row in df[df["provincia"].isin(ANOTAR)].iterrows():
        dx, dy = offsets.get(row["provincia"], (8, 4))
        ax.annotate(row["provincia"],
                    (row["informalidad_2025"], row["no_remunerado_2025"]),
                    textcoords="offset points", xytext=(dx, dy),
                    fontsize=9.5, color="#333333", zorder=4,
                    ha=ha_map.get(row["provincia"], "left"))

    ax.set_xlabel("Empleo en el sector informal (% del empleo total)", fontsize=10.5)
    ax.set_ylabel("Empleo no remunerado (% de la PEA)", fontsize=10.5)
    ax.set_title("Cada punto es una provincia. A mayor informalidad, mayor trabajo no remunerado.",
                 fontsize=11.5, loc="left", pad=10, color="#222222")
    ax.text(0.0, 1.005, f"Correlacion provincial r = {r:.2f} (descriptiva, no causal)",
            transform=ax.transAxes, fontsize=9, color="#777777")
    ax.legend(title="Region natural", frameon=False, fontsize=9.5,
              title_fontsize=9.5, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", color="#ebe8e2", lw=0.7, zorder=0)

    # --- Panel secundario: ranking ---
    ranked = df.sort_values("informalidad_2025")
    axb.barh(ranked["provincia"], ranked["informalidad_2025"],
             color=ranked["region_natural"].map(COLORES), height=0.72, zorder=3)
    axb.axvline(PROMEDIO_NACIONAL, color="#666666", lw=0.9, ls=":", zorder=4)
    axb.set_xlim(0, 95)
    axb.tick_params(axis="y", labelsize=8.2, length=0)
    axb.tick_params(axis="x", labelsize=8.5)
    axb.set_xlabel("Informalidad (%)", fontsize=9.5)
    axb.set_title("Ranking provincial vs. tasa nacional", fontsize=10.5,
                  loc="left", pad=10, color="#222222")
    axb.spines[["top", "right", "left"]].set_visible(False)
    axb.grid(axis="x", color="#ebe8e2", lw=0.7, zorder=0)

    # --- Titulos y pie ---
    fig.suptitle("La informalidad laboral en Ecuador no es una sola",
                 fontsize=18, fontweight="bold", x=0.06, ha="left", y=0.955,
                 color="#1a1a1a")
    fig.text(0.06, 0.875,
             "La informalidad se concentra en la Amazonia y la Sierra rural, donde coincide con altos niveles de empleo\n"
             "no remunerado: un patron de subsistencia, distinto de la informalidad urbana de provincias como Guayas.",
             fontsize=11.5, ha="left", color="#444444")
    fig.text(0.06, 0.02,
             "Fuente: INEC, ENEMDU anual 2025 (Boletin Tecnico N 03-2026-ENEMDU), Tablas 8 y 9.  "
             "Informalidad = empleo en unidades <100 trabajadores sin RUC.  "
             "Correlacion ecologica entre agregados provinciales, no entre individuos.",
             fontsize=8, ha="left", color="#888888")

    png = out_dir / "informalidad_ecuador.png"
    svg = out_dir / "informalidad_ecuador.svg"
    fig.savefig(png, dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(svg, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Figura guardada en:\n  {png}\n  {svg}")
    print(f"Correlacion r = {r:.3f}")
    return png


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera la figura desde un CSV.")
    ap.add_argument("--csv", default=str(CSV_REF), help="Ruta del CSV de entrada")
    args = ap.parse_args(argv)
    generar_grafico(args.csv)


if __name__ == "__main__":
    main()
