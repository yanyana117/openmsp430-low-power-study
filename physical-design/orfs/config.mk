# OpenROAD-flow-scripts design config: openMSP430 on sky130hd
#
# Usage (from OpenROAD-flow-scripts/flow, with OPENMSP430_ROOT set):
#   make DESIGN_CONFIG=$(OPENMSP430_ROOT)/physical-design/orfs/config.mk
#
# The floorplan variables at the bottom are sweep knobs. run_sweep.py overrides
# them per run via environment variables, so keep the ?= form.

export DESIGN_NICKNAME = openmsp430
export DESIGN_NAME     = openMSP430
export PLATFORM        = sky130hd

# RTL: the same sources used by the synthesis study in ../../rtl
export VERILOG_FILES = $(wildcard $(OPENMSP430_ROOT)/rtl/*.v)
export VERILOG_INCLUDE_DIRS = $(OPENMSP430_ROOT)/rtl
export VERILOG_DEFINES ?=

export SDC_FILE = $(OPENMSP430_ROOT)/physical-design/orfs/constraint.sdc

# The ORFS container enables Kepler LEC automatically when the binary exists.
# Keep this architectural exploration flow focused on PPA/floorplan results.
export LEC_CHECK = 0

# --- Floorplan sweep knobs (overridden by run_sweep.py) ---------------------
# Relative floorplan: utilization-driven (no fixed DIE/CORE area).
export CORE_UTILIZATION ?= 65
export CORE_ASPECT_RATIO ?= 1.0
export CORE_MARGIN       ?= 2
export PLACE_DENSITY     ?= 0.60

# Keep each sweep run in its own results/logs/reports subtree.
# run_sweep.py sets FLOW_VARIANT like: util65_ar10_pd060
export FLOW_VARIANT ?= base
