# openMSP430 Low-Power Clock-Gating: PPA Study and RTL-to-GDSII Physical Design

A two-part hardware study on the open-source **openMSP430** 16-bit microcontroller core:

1. **Clock-gating PPA and gate-level reliability study** (32 nm standard-cell library):
   compared an ungated baseline against three clock-gating configurations across
   workloads and process corners. Headline results: synthesis-inserted integrated
   clock gating (ICG) **reduced dynamic power by 74--81% and total power by 25--30%**
   across corners, and the study identified a gate-level failure in hand-written
   behavioral clock gates (functionally correct in RTL simulation, fails at gate
   level), root-caused to a hold race and confirmed with full SDF back-annotation.
2. **RTL-to-GDSII physical design extension** (this repository): the same core taken
   through the complete open-source **OpenROAD** flow on **sky130hd**, with a
   floorplan/routability exploration closed to a DRC- and antenna-clean final GDS.

> **Note on the study artifact.** The complete reproduction artifact for part 1
> (clock-gating RTL configurations, synthesis scripts, gate-level netlists, power
> reports, and the offline reproduction bundle) is temporarily private while the
> accompanying paper is under double-blind review at an IEEE conference, and will
> be re-released upon publication. This repository keeps the physical-design
> extension public in full.

## Physical design results

The best closed floorplan variant uses 30% target core utilization, 0.40 placement
density, and one-site placement padding; it generates final DEF/GDS with 0
detailed-route DRC violations and 0 antenna violations.

| Metric | Value |
| --- | ---: |
| Final setup WNS at 50 ns | 35.55 ns |
| Final hold WNS | 0.23 ns |
| Detailed-route DRC | 0 |
| Antenna violations | 0 net / 0 pin |
| Routed wirelength | 362,584 um |
| Total power | 0.0045 W |
| Estimated Fmax | 69.2 MHz |

The routability closure story: the default 65% utilization floorplan completed
global route cleanly but exposed met1/met2 pin-access and short violations in
detailed routing; lowering utilization alone reduced but did not eliminate DRC;
adding one-site placement padding at 30% utilization gave the detailed router
enough local whitespace to converge. A variant raising the minimum routing layer
to met2 was explored and dropped (it worsened routability pressure).

See [PHYSICAL_DESIGN_PLAN.md](PHYSICAL_DESIGN_PLAN.md) for the phase-by-phase plan
and [physical-design/results/summary.md](physical-design/results/summary.md) for
the full run data, variant table, and OpenROAD screenshots.

## Layout

- `physical-design/orfs/` — OpenROAD-flow-scripts design config and portable SDC
- `physical-design/sweep/` — floorplan-variant sweep runner, report parser, plots
- `physical-design/results/` — results CSV, summary, selected route/placement/IR
  images, and compact final artifacts (GDS, compressed DEF/netlist/SPEF)

## Tools

**OpenROAD / OpenSTA** (RTL-to-GDSII) on the **sky130hd** PDK via the official ORFS
Docker image. Part 1 used Synopsys VCS, Design Compiler, and PrimeTime PX with a
32 nm SAED32 library (artifact private during review, see note above).

## Third-party attribution

The **openMSP430** core is an open-source design by Olivier Girard (OpenCores),
distributed under the BSD license. The clock-gating study, the physical-design
flow, the floorplan exploration, and the tooling in this repository are my own work.
