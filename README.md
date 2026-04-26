# SKY130 DRC Automation Project

![drc-ci](https://github.com/abdo-ehab-euv/sky130-drc-automation/actions/workflows/drc-ci.yml/badge.svg)

A small Physical Verification project using **KLayout**, **Python**, **TCL**, and a real **SKY130 standard-cell GDS layout**.

This project runs a custom DRC rule deck on a SKY130 layout, exports KLayout DRC results to XML, parses the violations with Python, and generates an HTML dashboard with a summary table, violation chart, and violation details.

> This is a scoped educational DRC project, not a full production Calibre rule deck.

---

## Demo Screenshots

### SKY130 Layout Opened in KLayout

[![KLayout layout view](https://github.com/abdo-ehab-euv/sky130-drc-automation/raw/main/docs/images/klayout_layout.png)](/abdo-ehab-euv/sky130-drc-automation/blob/main/docs/images/klayout_layout.png)

### DRC Flow Running from PowerShell

[![Terminal DRC run](https://github.com/abdo-ehab-euv/sky130-drc-automation/raw/main/docs/images/terminal_run.png)](/abdo-ehab-euv/sky130-drc-automation/blob/main/docs/images/terminal_run.png)

### Generated HTML DRC Dashboard

[![HTML DRC report](https://github.com/abdo-ehab-euv/sky130-drc-automation/raw/main/docs/images/html_report.png)](/abdo-ehab-euv/sky130-drc-automation/blob/main/docs/images/html_report.png)

### Violation Chart

[![Violation chart](https://github.com/abdo-ehab-euv/sky130-drc-automation/raw/main/docs/images/violations_chart.png)](/abdo-ehab-euv/sky130-drc-automation/blob/main/docs/images/violations_chart.png)

---

## Project Result

The flow successfully ran on a SKY130 standard-cell layout.

| Metric | Result |
| --- | --- |
| Total rules checked | 4 |
| Rules passing | 3 |
| Rules failing | 1 |
| Total violations | 18 |

The failing rule was:

| Rule | Description | Violations |
| --- | --- | --- |
| MCON.A.1 | mcon minimum area violation: area < 0.2025 um² | 18 |

The other rules passed with zero violations:

| Rule | Description | Status |
| --- | --- | --- |
| LI.W.1 | li1 minimum width < 0.17 um | PASS |
| LI.S.1 | li1 minimum spacing < 0.17 um | PASS |
| NW.ENC.1 | nwell enclosure of nsdm < 0.125 um | PASS |

A sample generated report is included here:

[Open sample DRC HTML report](https://github.com/abdo-ehab-euv/sky130-drc-automation/blob/main/docs/sample_drc_report.html)

---

## What This Project Does

The project automates a mini Physical Verification flow:

1. Loads a GDS layout into KLayout.
2. Runs custom DRC rules.
3. Exports violations to `results.xml`.
4. Parses the XML results using Python.
5. Generates:
   * terminal summary table
   * violation bar chart
   * HTML dashboard

---

## Why DRC Matters

DRC, or Design Rule Checking, verifies that an IC layout follows the physical manufacturing constraints of a process technology.

Examples of DRC checks include:

* minimum wire width
* minimum spacing between shapes
* layer enclosure
* minimum polygon area

In a real semiconductor flow, DRC is required before tapeout because layout violations can cause manufacturing failures.

---

## Tool Stack

| Tool | Purpose |
| --- | --- |
| KLayout | Layout viewer and DRC engine |
| Python | Automation and report generation |
| TCL | Optional batch automation script |
| SKY130 | Open-source 130 nm PDK/layout data |
| Git/GitHub | Project version control and portfolio display |



---

## Files

| File | Purpose |
| --- | --- |
| `drc_rules.drc` | Custom KLayout DRC rule deck |
| `run_drc.py` | Python script that runs KLayout DRC in batch mode |
| `analyze_results.py` | Parses DRC XML and generates report files |
| `run_drc.tcl` | Optional TCL batch automation script |
| `requirements.txt` | Python package dependencies |
| `README.md` | Project documentation |
| `docs/images/` | Screenshots and report images |
| `docs/sample_drc_report.html` | Example generated report |
| `advanced/openlane/` | RTL-to-GDSII demo (4-bit adder + OpenLane config) |
| `advanced/lvs/` | Educational LVS demo (resistor netlist comparator) |
| `advanced/rules/` | Expanded SKY130-style DRC rule deck |
| `advanced/ci/` | CI helper notes |
| `.github/workflows/drc-ci.yml` | GitHub Actions CI pipeline |



---

## DRC Rules Implemented

| Rule ID | Layer(s) | Check | Limit |
| --- | --- | --- | --- |
| LI.W.1 | li1 `67/20` | Minimum width | 0.17 um |
| LI.S.1 | li1 `67/20` | Minimum spacing | 0.17 um |
| NW.ENC.1 | nwell `64/20`, nsdm `93/44` | nwell enclosure of nsdm | 0.125 um |
| MCON.A.1 | mcon `67/44` | Minimum area | 0.2025 um² |



---

## Setup

Install Python dependencies:

```
python -m pip install -r requirements.txt
```

---

## Advanced Extensions

These extensions build on top of the core DRC flow without changing it.
Everything new lives under `advanced/`, `docs/`, and `.github/`.

```
RTL Verilog
   ↓
OpenLane Flow
   ↓
GDSII Layout
   ↓
KLayout DRC
   ↓
Python XML Parser
   ↓
HTML Report + CI Artifacts
```

### RTL-to-GDSII OpenLane Demo

A tiny 4-bit adder in [`advanced/openlane/src/adder4.v`](advanced/openlane/src/adder4.v)
plus an OpenLane [`config.json`](advanced/openlane/config.json) targeting
`sky130_fd_sc_hd`. Walks RTL → synthesis → P&R → GDSII, after which the
generated GDS feeds the same DRC flow as the rest of the repo.

OpenLane is **not required** to use the rest of the project — it is a
demonstration of how the full flow looks. See
[`docs/ADVANCED_FLOW.md`](docs/ADVANCED_FLOW.md) for a step-by-step
walkthrough and [`advanced/openlane/README.md`](advanced/openlane/README.md)
for run instructions on Docker / WSL2 / Linux.

### LVS Educational Demo

A miniature Layout-Versus-Schematic comparator that takes two
resistor-only SPICE netlists and reports PASS / FAIL on devices, values,
and connectivity. See
[`docs/LVS_DEMO.md`](docs/LVS_DEMO.md).

```bash
# PASS — schematic and "extracted" netlists describe the same circuit
python advanced/lvs/lvs_compare.py advanced/lvs/resistor_network.spice advanced/lvs/resistor_network_extracted.spice

# FAIL — bump the first resistor 10% in memory to demonstrate that
# the comparator catches a real difference
python advanced/lvs/lvs_compare.py advanced/lvs/resistor_network.spice advanced/lvs/resistor_network_extracted.spice --inject-mismatch
```

### Expanded SKY130-Style DRC Rules

Six more rules covering metal1, poly, mcon enclosure, and nwell spacing,
with a JSON manifest documenting every value's source. Read
[`docs/RULE_EXPANSION.md`](docs/RULE_EXPANSION.md) for the full table.

```powershell
# Use the existing run_drc.py with the extra deck (Windows PowerShell)
python run_drc.py --klayout "C:\Users\iamth\AppData\Roaming\KLayout\klayout_app.exe" --rules advanced\rules\sky130_extra_rules.lydrc --input layout.gds --output results_extra.xml --analyze
```

The same command, on macOS / Linux / WSL:

```bash
python run_drc.py --rules advanced/rules/sky130_extra_rules.lydrc --input layout.gds --output results_extra.xml --analyze
```

And the original core flow still works exactly as before:

```powershell
python run_drc.py --klayout "C:\Users\iamth\AppData\Roaming\KLayout\klayout_app.exe" --input layout.gds --output results.xml --analyze
```

### GitHub Actions CI

[`.github/workflows/drc-ci.yml`](.github/workflows/drc-ci.yml) runs on
every push and pull request. It installs the Python deps, syntax-checks
every script, runs the LVS demo in both PASS and FAIL modes, validates
the rule manifest, and uploads any generated reports as artifacts.

KLayout itself is not installed in CI today; see
[`docs/CI_PIPELINE.md`](docs/CI_PIPELINE.md) for how to add it via a
container image later.
