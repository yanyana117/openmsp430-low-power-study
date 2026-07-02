# Clock constraint for openMSP430 on sky130hd.
#
# Starting point: 20 MHz (50 ns), a comfortable target for MSP430-class cores on
# sky130hd. The physical-design closure loop keeps this clock fixed and uses
# floorplan/placement knobs to recover routability.

set clk_name  dco_clk
set clk_port  [get_ports dco_clk]
set clk_period 50.0
if {[info exists ::env(CLOCK_PERIOD_NS)]} {
  set clk_period $::env(CLOCK_PERIOD_NS)
}

create_clock -name $clk_name -period $clk_period $clk_port

# First-pass internal timing constraint for the RTL-to-GDSII bring-up.
# I/O delays are intentionally omitted until the baseline flow is closed; this
# keeps the OpenROAD/OpenSTA SDC portable across flow stages and focuses the
# floorplan sweep on internal setup timing, area, wirelength, congestion, and DRC.
