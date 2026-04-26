# OpenLane RTL-to-GDSII Demo

This folder contains a tiny **4-bit adder** Verilog design and an
OpenLane-style `config.json` so you can take a piece of RTL all the way
through synthesis, placement, routing, and GDSII export — and then run the
project's KLayout DRC rule deck on the resulting GDS.

> ⚠️ OpenLane is **not** required to install just to use this repo. If you
> do not have OpenLane, this folder still serves as a clear example of what
> the front of a real PV flow looks like. The DRC scripts in the parent
> repo work on **any** SKY130 GDS — including the `layout.gds` already
> committed here.

---

## Files

| File              | Purpose                                                    |
|-------------------|------------------------------------------------------------|
| `src/adder4.v`    | 4-bit ripple-carry adder Verilog source                    |
| `config.json`     | OpenLane configuration targeting `sky130_fd_sc_hd`         |
| `README.md`       | This file                                                  |

## How this connects to the rest of the project

```
Verilog RTL  ──►  OpenLane (synthesis + P&R)  ──►  GDSII layout
                                                      │
                                                      ▼
                                             KLayout DRC rule deck
                                                      │
                                                      ▼
                                       Python XML parser + HTML report
```

Today, the repo's `layout.gds` is a hand-picked SKY130 standard-cell layout.
The OpenLane demo lets you **generate your own GDS** from RTL and then
verify it with the same DRC scripts.

## High-level run instructions

OpenLane is most easily run inside Docker (or WSL2 on Windows). The
canonical way to run it is via the official `openlane` command from
[The OpenROAD Project's OpenLane2](https://github.com/efabless/openlane2).

```bash
# 1. Install OpenLane (Linux, macOS, or WSL2)
pip install openlane

# 2. From the project root, run the flow on this design
openlane advanced/openlane/config.json
```

The classic Make-based flow looks like this instead:

```bash
# Inside the OpenLane container
./flow.tcl -design /path/to/sky130-drc-automation/advanced/openlane
```

## Where the final GDS appears

After a successful run, OpenLane writes the routed GDS to (path varies
slightly by OpenLane version):

```
runs/<run_tag>/results/final/gds/adder4.gds
```

…or, with OpenLane 2:

```
runs/RUN_<timestamp>/final/gds/adder4.gds
```

## Feeding the OpenLane GDS into the project's DRC flow

Once you have `adder4.gds`, copy it next to the existing `layout.gds`
(or use `--input` directly):

```powershell
# From the repo root, on Windows PowerShell
Copy-Item runs\<run_tag>\results\final\gds\adder4.gds .\layout.gds

python run_drc.py --klayout "C:\Users\iamth\AppData\Roaming\KLayout\klayout_app.exe" `
                  --input  layout.gds `
                  --output results.xml `
                  --analyze
```

That single command runs the same KLayout DRC + Python report flow on the
GDS your own RTL just produced — closing the loop from Verilog to a
verified, manufacturable layout.

## Caveats

- The OpenLane defaults in `config.json` are deliberately permissive. Real
  SoC blocks need power-domain, CTS, and signoff configuration that is
  outside the scope of this educational demo.
- A 4-bit adder is too small to expose interesting routing congestion or
  sign-off violations. Treat it as a smoke-test of the flow, not as a
  representative DRC workload.
- See [`docs/ADVANCED_FLOW.md`](../../docs/ADVANCED_FLOW.md) for the broader
  RTL-to-DRC narrative.
