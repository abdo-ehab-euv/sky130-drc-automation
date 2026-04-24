#!/usr/bin/env tclsh
# =============================================================================
# run_drc.tcl
# Simple TCL wrapper that invokes KLayout in batch mode on a SKY130 GDS.
# =============================================================================
#
# Usage:
#   tclsh run_drc.tcl
#
# Edit the three variables below if your filenames differ.
# =============================================================================

set input_gds   "layout.gds"
set output_xml  "results.xml"
set drc_script  "drc_rules.lydrc"

# Build the KLayout command exactly as run_drc.py builds it so both flows
# use the same variable names ($input, $output) expected by drc_rules.lydrc.
set cmd [list klayout -b -r $drc_script \
                      -rd "input=$input_gds" \
                      -rd "output=$output_xml"]

puts "Running: $cmd"

if {[catch {exec {*}$cmd} result options]} {
    puts stderr "ERROR: KLayout DRC failed."
    puts stderr $result
    exit 1
}

puts "DRC complete. Results written to $output_xml"
