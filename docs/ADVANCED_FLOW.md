# Advanced Flow: RTL → GDSII → DRC → Report

This document describes how the pieces of the project fit together once
the OpenLane demo is wired in. The core repo only covers the right-hand
half (DRC + reporting). The OpenLane demo adds the left-hand half (RTL
synthesis through to GDSII).

```
┌───────────────────┐
│  Verilog RTL      │   advanced/openlane/src/adder4.v
│  (your design)    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  OpenLane         │   synthesis (Yosys) + placement/routing (OpenROAD)
│  RTL → GDSII      │   advanced/openlane/config.json
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  GDSII layout     │   runs/<tag>/results/final/gds/adder4.gds
│  (sky130A)        │   →  copy to ./layout.gds
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  KLayout DRC      │   drc_rules.lydrc  (core)
│  rule deck        │   advanced/rules/sky130_extra_rules.lydrc  (extra)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  results.xml      │   KLayout report database
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Python analyzer  │   analyze_results.py
│                   │   →  drc_report.html, violations.png
└───────────────────┘
```

## Why this matters

In industry, "physical verification" is the **last** stage before
tapeout, but it cannot do its job in isolation. Front-end designers care
about whether their RTL changes will *cause* DRC violations downstream,
and PV engineers need to be able to re-run sign-off on a new GDS as soon
as P&R produces one.

The OpenLane demo here lets you:

1. Edit `adder4.v` (or drop in your own design).
2. Re-run OpenLane to produce a new `adder4.gds`.
3. Re-run the existing `run_drc.py --analyze` flow on that GDS.
4. See PASS/FAIL change in the HTML dashboard.

That round-trip is exactly the design-DRC iteration loop a PV engineer
does in production, just with smaller blocks and open-source tools.

## What you don't get from this demo

- Real timing closure or static-timing analysis (STA).
- Power and ground planning at the chip level.
- Multi-clock or multi-power-domain handling.
- Antenna effect or CMP density signoff.

These are areas to expand into once the basic loop is comfortable. The
[OpenLane documentation](https://openlane2.readthedocs.io/en/latest/)
walks through them in order.
