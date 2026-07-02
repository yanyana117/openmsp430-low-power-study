#!/usr/bin/env python3
"""Floorplan/routability sweep runner for openMSP430 on OpenROAD-flow-scripts.

Runs the exact variant sequence from the closure study (see results/summary.md),
each under its own FLOW_VARIANT so results/logs/reports stay separate.

Usage (inside the ORFS container, or against a local ORFS checkout):
    python3 run_sweep.py --orfs /OpenROAD-flow-scripts [--only util30_ar10_pd040_pad1] [--dry-run]

The Docker invocation that wraps this is documented in physical-design/README.md.
Requires OPENMSP430_ROOT to be set (or inferred from this file's location).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_MK = REPO_ROOT / "physical-design" / "orfs" / "config.mk"

# The variants actually run in the routability-closure study, in study order.
# Values not listed fall back to the ?= defaults in orfs/config.mk.
CONFIGS = [
    {"FLOW_VARIANT": "base"},  # defaults: util 65, AR 1.0, density 0.60
    {"FLOW_VARIANT": "util45_ar10_pd050",
     "CORE_UTILIZATION": "45", "PLACE_DENSITY": "0.50"},
    {"FLOW_VARIANT": "util35_ar10_pd045",
     "CORE_UTILIZATION": "35", "PLACE_DENSITY": "0.45"},
    {"FLOW_VARIANT": "util35_ar10_pd045_m2",
     "CORE_UTILIZATION": "35", "PLACE_DENSITY": "0.45",
     "MIN_ROUTING_LAYER": "met2"},  # explored and dropped: worsened routability
    {"FLOW_VARIANT": "util30_ar10_pd040_pad1",  # the clean-GDS closure run
     "CORE_UTILIZATION": "30", "PLACE_DENSITY": "0.40", "CORE_MARGIN": "8",
     "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT": "1",
     "CELL_PAD_IN_SITES_DETAIL_PLACEMENT": "1"},
]


def run_one(flow_dir: Path, cfg: dict, dry_run: bool) -> bool:
    variant = cfg["FLOW_VARIANT"]
    env = os.environ.copy()
    env["OPENMSP430_ROOT"] = str(REPO_ROOT)
    env.update(cfg)
    cmd = ["make", f"DESIGN_CONFIG={CONFIG_MK}"]
    overrides = " ".join(f"{k}={v}" for k, v in cfg.items() if k != "FLOW_VARIANT")
    print(f"[sweep] {variant}: {' '.join(cmd)}  ({overrides or 'config.mk defaults'})")
    if dry_run:
        return True
    log_path = flow_dir / f"sweep_{variant}.log"
    with open(log_path, "w") as log:
        proc = subprocess.run(cmd, cwd=flow_dir, env=env, stdout=log, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0
    print(f"[sweep] {variant}: {'OK' if ok else f'FAILED (see {log_path})'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--orfs", required=True, help="Path to OpenROAD-flow-scripts checkout")
    ap.add_argument("--only", help="Run a single FLOW_VARIANT from the study list")
    ap.add_argument("--dry-run", action="store_true", help="Print commands without running")
    args = ap.parse_args()

    flow_dir = Path(args.orfs).expanduser().resolve() / "flow"
    if not (flow_dir / "Makefile").exists():
        sys.exit(f"error: {flow_dir} does not look like an ORFS flow directory")

    configs = [c for c in CONFIGS if not args.only or c["FLOW_VARIANT"] == args.only]
    if not configs:
        sys.exit(f"error: unknown variant {args.only!r}; choices: "
                 + ", ".join(c["FLOW_VARIANT"] for c in CONFIGS))

    results = {c["FLOW_VARIANT"]: run_one(flow_dir, c, args.dry_run) for c in configs}
    failed = [v for v, ok in results.items() if not ok]
    print(f"\n[sweep] done: {len(results) - len(failed)}/{len(results)} succeeded")
    if failed:
        print("[sweep] failed variants:", ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
