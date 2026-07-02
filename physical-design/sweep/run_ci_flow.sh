#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d /OpenROAD-flow-scripts/flow ]]; then
  echo "error: /OpenROAD-flow-scripts/flow not found" >&2
  exit 2
fi
if [[ ! -d /work ]]; then
  echo "error: /work repo mount not found" >&2
  exit 2
fi

source /OpenROAD-flow-scripts/env.sh
cd /OpenROAD-flow-scripts/flow

design_config=/work/physical-design/orfs/config.mk
export OPENMSP430_ROOT=/work

echo "[orfs] baseline RTL-to-GDSII"
make DESIGN_CONFIG="$design_config" FLOW_VARIANT=base

echo "[orfs] floorplan sweep"
python3 /work/physical-design/sweep/run_sweep.py --orfs /OpenROAD-flow-scripts

echo "[orfs] opt1 gated post-route run"
make DESIGN_CONFIG="$design_config" FLOW_VARIANT=opt1_gated VERILOG_DEFINES="-D CG_ENABLE"

echo "[orfs] finished baseline, sweep, and gated runs"
