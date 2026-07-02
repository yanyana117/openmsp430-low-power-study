# Physical Design Extension Plan — Floorplan Exploration on openMSP430

**Status**: baseline OpenROAD RTL-to-GDSII closure complete; clock-gated post-route
comparison remains future work.

## Goal

Extend this study from synthesis-level PPA (Design Compiler + PrimeTime PX, 32 nm) down to
**full RTL-to-GDSII physical design** with the open-source **OpenROAD** flow, and run a
systematic **floorplan exploration**: how do core utilization, aspect ratio, and placement
density change timing (WNS/TNS), routing congestion, wirelength, area, and power?

Two things make this a natural extension rather than a new project:

1. The clock-gating variants studied at synthesis level here get re-measured **after
   placement and routing**, closing the loop the original study left open (synthesis-level
   power numbers vs. post-route reality).
2. The sweep is driven by a small Python tool built for this repo — config generation,
   batch flow execution, report parsing, and trade-off plots — i.e. flow/tool
   infrastructure work, not just tool usage.

## Flow and platform

- **Flow**: [OpenROAD-flow-scripts (ORFS)](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts),
  run via the official Docker image (no EDA licenses needed).
- **Platform**: `sky130hd` (SkyWater 130 nm HD standard cells) as primary;
  `nangate45` as a sanity cross-check if time allows.
- **Design**: the same openMSP430 RTL in `rtl/`, top module `openMSP430`,
  baseline configuration first, clock-gated variant (`opt1`) second.

## Phases

### Phase 1 — Baseline RTL-to-GDSII
- [x] Install ORFS via Docker and verify the toolchain in the container
- [x] Write `physical-design/orfs/config.mk` + `constraint.sdc` for openMSP430 on sky130hd
- [x] Run the full flow: synth → floorplan → place → CTS → route → finish
- [x] Record baseline metrics (WNS/TNS, area, utilization, wirelength, power) and final-route images

### Phase 2 — Floorplan sweep tool
- [x] `run_sweep.py`: generate config variants with a distinct `FLOW_VARIANT`
- [x] `parse_reports.py`: scrape ORFS JSON logs into one CSV (one row per variant)
- [x] `plot_results.py`: area-vs-WNS Pareto plot, congestion heatmap by utilization
- [x] Targeted sweep: baseline, 45% util, 35% util, 35% util with met2 minimum routing, and the final 30% util / 0.40 density / 1-site padding closure run
- [x] Written findings in `physical-design/results/summary.md`

### Phase 3 — Floorplan/routability closure exercise
- [x] Identify the initial routing bottleneck at high utilization
- [x] Recover detailed-route closure using floorplan/placement knobs only: utilization, placement density, core margin, and one-site cell padding
- [x] Document the closure loop and final metrics

### Phase 4 — Clock-gating closes the loop (future work)
- [ ] Run the `opt1` clock-gated variant through the same flow
- [ ] Compare post-route power vs. the synthesis-level numbers reported in the original study
- [ ] One-page summary table: baseline vs. gated, synthesis vs. post-route

## Directory layout

```
physical-design/
  README.md            quickstart + status
  orfs/
    config.mk          ORFS design config (sky130hd, openMSP430)
    constraint.sdc     clock constraint
  sweep/
    run_sweep.py       config generation + batch flow execution
    parse_reports.py   ORFS reports -> results.csv
    plot_results.py    Pareto / heatmap plots
  results/             checked-in CSVs, summary, images, and compact final artifacts
```

## Metrics collected per run

| Metric | Source |
|---|---|
| WNS / TNS (setup) | OpenSTA final timing report |
| Core / die area, utilization | floorplan + finish reports |
| Total wirelength | detailed route report |
| DRC violation count | detailed route log |
| Total / leakage power | final power report |
| Runtime per stage | flow logs |

## Ground rules

- Every commit authored and committed by Xingran Huang <yanyana117@gmail.com>; no AI
  co-author trailers (see career repo GIT_COMMIT_RULES.md).
- Results in the README must be reproducible from the checked-in configs alone.
- No claim lands in the resume until the corresponding phase is actually done.
