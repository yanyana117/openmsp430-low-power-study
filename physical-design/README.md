# Physical Design: openMSP430 RTL-to-GDSII + Floorplan Exploration

Extension of the synthesis-level study in the repo root: the same openMSP430 core is taken
through the full open-source **OpenROAD** flow (synthesis → floorplan → place → CTS →
route → GDSII) on **sky130hd**, followed by a scripted floorplan sweep that quantifies
area / timing / congestion trade-offs. See [PHYSICAL_DESIGN_PLAN.md](../PHYSICAL_DESIGN_PLAN.md)
for the full plan and status.

## Status

- [x] Baseline RTL-to-GDSII on sky130hd
- [x] Floorplan/routability sweep tooling and report parsing
- [x] Floorplan-parameter closure loop for a clean detailed route
- [ ] Clock-gated variant post-route power vs. synthesis-level numbers

## Best Closed Run

| Metric | Value |
| --- | ---: |
| Variant | `util30_ar10_pd040_pad1` |
| Target utilization / placement density | 30% / 0.40 |
| Placement padding | 1 site |
| Final setup WNS at 50 ns | 35.55 ns |
| Final hold WNS | 0.23 ns |
| Final TNS | 0.00 ns |
| Detailed-route DRC | 0 |
| Antenna violations | 0 net / 0 pin |
| Routed wirelength | 362,584 um |
| Total power | 0.0045 W |
| Final artifacts | DEF, GDS, Verilog, SDC, SPEF generated locally; selected artifacts are checked in under `results/` |

## Quickstart

1. Install Docker and pull the ORFS image:

   ```sh
   docker pull --platform linux/amd64 openroad/orfs:latest
   ```

2. Run the closed floorplan variant:

   ```sh
   cd /path/to/openmsp430-low-power-study
   mkdir -p physical-design/orfs-work/{logs,reports,results,objects}
   docker run --rm --platform linux/amd64 \
     -v "$PWD:/work" \
     -v "$PWD/physical-design/orfs-work/logs:/OpenROAD-flow-scripts/flow/logs" \
     -v "$PWD/physical-design/orfs-work/reports:/OpenROAD-flow-scripts/flow/reports" \
     -v "$PWD/physical-design/orfs-work/results:/OpenROAD-flow-scripts/flow/results" \
     -v "$PWD/physical-design/orfs-work/objects:/OpenROAD-flow-scripts/flow/objects" \
     openroad/orfs:latest \
     bash -lc 'source /OpenROAD-flow-scripts/env.sh && cd /OpenROAD-flow-scripts/flow && \
       export OPENMSP430_ROOT=/work && \
       CORE_UTILIZATION=30 CORE_ASPECT_RATIO=1.0 CORE_MARGIN=8 PLACE_DENSITY=0.40 \
       CELL_PAD_IN_SITES_GLOBAL_PLACEMENT=1 CELL_PAD_IN_SITES_DETAIL_PLACEMENT=1 \
       FLOW_VARIANT=util30_ar10_pd040_pad1 \
       make DESIGN_CONFIG=/work/physical-design/orfs/config.mk'
   ```

3. Collect results:

   ```sh
   python3 physical-design/sweep/parse_reports.py \
     --flow-dir physical-design/orfs-work \
     -o physical-design/results/results.csv

   # Optional plotting helper.
   python3 -m pip install matplotlib
   python3 physical-design/sweep/plot_results.py physical-design/results/results.csv
   ```

## Layout

- `orfs/` — ORFS design config (`config.mk`) and clock constraint (`constraint.sdc`)
- `sweep/` — sweep runner, report parser, plotting
- `results/` — checked-in CSVs, summary, selected OpenROAD images, and final GDS / compressed DEF
- `orfs-work/` — local Docker-mounted ORFS logs/results cache, gitignored
