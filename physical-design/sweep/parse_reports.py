#!/usr/bin/env python3
"""Collect per-variant metrics from OpenROAD-flow-scripts runs into one CSV.

Walks <orfs>/flow/logs/sky130hd/openmsp430/<variant>/ or a local
physical-design/orfs-work mirror and extracts timing, area, wirelength, DRC,
antenna, power, and final-artifact status from ORFS's per-stage JSON logs.

Usage:
    python3 parse_reports.py --orfs /path/to/OpenROAD-flow-scripts -o results/results.csv
    python3 parse_reports.py --flow-dir physical-design/orfs-work -o results/results.csv

Unmatched fields are left blank rather than guessed, so a blank cell means
"check that run by hand".
"""

import argparse
import csv
import json
import sys
from pathlib import Path

PLATFORM = "sky130hd"
DESIGN = "openmsp430"

FIELDNAMES = [
    "variant",
    "status",
    "setup_wns_ns",
    "hold_wns_ns",
    "tns_ns",
    "fmax_mhz",
    "die_area_um2",
    "core_area_um2",
    "stdcell_area_um2",
    "utilization_pct",
    "global_route_wirelength_um",
    "detail_route_wirelength_um",
    "drc_count",
    "antenna_net_violations",
    "antenna_pin_violations",
    "total_power_w",
    "vdd_worst_ir_drop_v",
    "final_gds",
]


def read_jsons(variant_dir: Path) -> dict:
    metrics = {}
    for f in sorted(variant_dir.glob("*.json")):
        try:
            metrics.update(json.loads(f.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return metrics


def first(metrics: dict, *keys: str):
    for key in keys:
        if key in metrics:
            return metrics[key]
    return None


def fmt(value, scale: float = 1.0, precision: int = 3) -> str:
    if value is None:
        return ""
    try:
        number = float(value) * scale
    except (TypeError, ValueError):
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.{precision}f}".rstrip("0").rstrip(".")


def status(metrics: dict, result_dir: Path) -> str:
    drc = first(metrics, "detailedroute__route__drc_errors")
    ant_nets = first(metrics, "detailedroute__antenna__violating__nets")
    ant_pins = first(metrics, "detailedroute__antenna__violating__pins")
    if result_dir.joinpath("6_final.gds").exists() and drc == 0 and ant_nets == 0 and ant_pins == 0:
        return "clean final GDS"
    if drc is not None:
        return "detail route explored"
    if "globalroute__design__violations" in metrics:
        return "global route complete"
    if "cts__timing__setup__ws" in metrics or "cts__design__instance__count" in metrics:
        return "CTS complete"
    if "globalplace__timing__setup__ws" in metrics:
        return "placement complete"
    if "floorplan__design__core__area" in metrics:
        return "floorplan complete"
    return "partial"


def row_for(variant: str, log_dir: Path, result_dir: Path) -> dict:
    metrics = read_jsons(log_dir)
    fmax_hz = first(
        metrics,
        "finish__timing__fmax",
        "globalroute__timing__fmax",
        "cts__timing__fmax",
        "floorplan__timing__fmax",
    )
    utilization = first(
        metrics,
        "finish__design__instance__utilization",
        "globalroute__design__instance__utilization",
        "detailedroute__utilizatin__before__dpl",
        "floorplan__design__instance__utilization",
    )
    if utilization is not None and float(utilization) <= 1.0:
        utilization = float(utilization) * 100.0

    return {
        "variant": variant,
        "status": status(metrics, result_dir),
        "setup_wns_ns": fmt(first(metrics, "finish__timing__setup__ws", "globalroute__timing__setup__ws", "floorplan__timing__setup__ws")),
        "hold_wns_ns": fmt(first(metrics, "finish__timing__hold__ws", "globalroute__timing__hold__ws", "floorplan__timing__hold__ws")),
        "tns_ns": fmt(first(metrics, "finish__timing__setup__tns", "globalroute__timing__setup__tns", "floorplan__timing__setup__tns")),
        "fmax_mhz": fmt(fmax_hz, scale=1e-6),
        "die_area_um2": fmt(first(metrics, "finish__design__die__area", "globalroute__design__die__area", "floorplan__design__die__area")),
        "core_area_um2": fmt(first(metrics, "finish__design__core__area", "globalroute__design__core__area", "floorplan__design__core__area")),
        "stdcell_area_um2": fmt(first(metrics, "finish__design__instance__area__stdcell", "globalroute__design__instance__area__stdcell", "floorplan__design__instance__area__stdcell")),
        "utilization_pct": fmt(utilization),
        "global_route_wirelength_um": fmt(first(metrics, "globalroute__global_route__wirelength")),
        "detail_route_wirelength_um": fmt(first(metrics, "detailedroute__route__wirelength")),
        "drc_count": fmt(first(metrics, "detailedroute__route__drc_errors")),
        "antenna_net_violations": fmt(first(metrics, "detailedroute__antenna__violating__nets", "globalroute__antenna__violating__nets")),
        "antenna_pin_violations": fmt(first(metrics, "detailedroute__antenna__violating__pins", "globalroute__antenna__violating__pins")),
        "total_power_w": fmt(first(metrics, "finish__power__total", "globalroute__power__total", "floorplan__power__total"), precision=8),
        "vdd_worst_ir_drop_v": fmt(first(metrics, "finish__design_powergrid__drop__worst__net:VDD__corner:default"), precision=8),
        "final_gds": "yes" if result_dir.joinpath("6_final.gds").exists() else "",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--orfs", help="Path to OpenROAD-flow-scripts checkout")
    ap.add_argument("--flow-dir", help="Path containing ORFS logs/ and reports/ directories")
    ap.add_argument("-o", "--out", default="results/results.csv")
    args = ap.parse_args()
    if not args.orfs and not args.flow_dir:
        sys.exit("error: pass either --orfs or --flow-dir")

    flow_root = Path(args.flow_dir).expanduser() if args.flow_dir else Path(args.orfs).expanduser() / "flow"

    log_root = flow_root / "logs" / PLATFORM / DESIGN
    result_root = flow_root / "results" / PLATFORM / DESIGN
    rows = []
    if log_root.is_dir():
        for variant_dir in sorted(p for p in log_root.iterdir() if p.is_dir()):
            rows.append(row_for(variant_dir.name, variant_dir, result_root / variant_dir.name))

    if not rows:
        sys.exit("error: no variant directories found - check --orfs path and that runs completed")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[parse] wrote {len(rows)} rows -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
