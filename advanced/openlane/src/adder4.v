// =============================================================================
// adder4.v
// A simple 4-bit ripple-carry adder used as the RTL example for the
// OpenLane RTL-to-GDSII demo.
// =============================================================================
//
// Inputs : a[3:0], b[3:0], cin
// Outputs: sum[3:0], cout
//
// This module is intentionally tiny so OpenLane can synthesise it quickly
// on a laptop. The whole point is to exercise the flow end-to-end, not to
// design a high-performance adder.
// =============================================================================

`default_nettype none

module adder4 (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire       cin,
    output wire [3:0] sum,
    output wire       cout
);

    // 5-bit add; high bit is the carry-out.
    wire [4:0] result;
    assign result = a + b + cin;

    assign sum  = result[3:0];
    assign cout = result[4];

endmodule

`default_nettype wire
