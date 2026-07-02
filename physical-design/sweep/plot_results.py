#!/usr/bin/env python3
"""Plot floorplan sweep trade-offs from results.csv.

Produces:
  results/pareto_area_wns.png   core area vs setup WNS scatter
  results/heatmap_wns.png       setup WNS by utilization x aspect ratio

Usage:
    python3 plot_results.py results/results.csv
"""

import csv
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

VARIANT_RX = re.compile(r"util(\d+)_ar(\d+)")


def load(path: str):
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            m = VARIANT_RX.search(row["variant"])
            if not m:
                continue
            try:
                rows.append({
                    "util": int(m.group(1)),
                    "ar": int(m.group(2)) / 10.0,
                    "wns": float((row.get("setup_wns_ns") or row.get("wns_ns") or "nan")),
                    "area": float((row.get("core_area_um2") or row.get("core_area") or "nan")),
                })
            except ValueError:
                continue
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = load(sys.argv[1])
    if not rows:
        sys.exit("error: no parsable rows in CSV")
    outdir = Path(sys.argv[1]).parent

    # Pareto: area vs WNS, one point per variant
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for r in rows:
        ax.scatter(r["area"], r["wns"], s=60)
        ax.annotate(f"u{r['util']}/ar{r['ar']}", (r["area"], r["wns"]), fontsize=7,
                    xytext=(4, 4), textcoords="offset points")
    ax.axhline(0, lw=0.8, ls="--")
    ax.set_xlabel("Core area (um^2)")
    ax.set_ylabel("WNS (ns)")
    ax.set_title("openMSP430 sky130hd: floorplan area vs setup slack")
    fig.tight_layout()
    fig.savefig(outdir / "pareto_area_wns.png", dpi=160)

    # Heatmap: WNS over the sweep grid
    utils = sorted({r["util"] for r in rows})
    ars = sorted({r["ar"] for r in rows})
    grid = [[next((r["wns"] for r in rows if r["util"] == u and r["ar"] == a), float("nan"))
             for a in ars] for u in utils]
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(grid, aspect="auto")
    ax.set_xticks(range(len(ars)), [str(a) for a in ars])
    ax.set_yticks(range(len(utils)), [f"{u}%" for u in utils])
    ax.set_xlabel("Aspect ratio")
    ax.set_ylabel("Core utilization")
    ax.set_title("WNS (ns) across the floorplan sweep")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(outdir / "heatmap_wns.png", dpi=160)

    print(f"[plot] wrote pareto_area_wns.png and heatmap_wns.png -> {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
