# SKY130 DRC Automation & Physical Verification Dashboard

![drc-ci](https://github.com/abdo-ehab-euv/sky130-drc-automation/actions/workflows/drc-ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![KLayout](https://img.shields.io/badge/DRC_Engine-KLayout-orange)
![SKY130](https://img.shields.io/badge/PDK-SKY130-green)

Automated SKY130-style DRC flow that runs custom physical design rule checks
on a GDS layout using KLayout in batch mode, exports violations to XML,
parses the results with Python, and generates an HTML dashboard for
debugging and documentation.

> **Scope note** — This is an educational physical-verification project,
> not a production signoff deck. The goal is to demonstrate DRC automation,
> rule-deck scripting, result parsing, and EDA flow integration — skills
> used daily by physical design and physical verification engineers.

---

## Project Highlights

| Aspect              | Detail                                                           |
|----------------------|------------------------------------------------------------------|
| **Flow**             | GDS → KLayout batch DRC → XML report → Python parser → dashboard |
| **Input layout**     | `layout.gds` — SKY130 `sky130_fd_sc_hd__a2111o_1` standard cell |
| **DRC engine**       | KLayout (batch mode, `-b -r`)                                    |
| **Rule format**      | KLayout `.lydrc` / `.drc` rule-deck scripting                    |
| **Rules implemented**| 4 core + 6 extended SKY130-style checks (10 total)               |
| **Output format**    | KLayout XML / RDB violation database                             |
| **Parser**           | `analyze_results.py` — XML → summary + chart + HTML              |
| **Dashboard**        | Self-contained HTML report with violation table and bar chart     |
| **CI**               | GitHub Actions — syntax checks, LVS demo, manifest validation    |
| **Advanced**         | OpenLane RTL→GDSII demo, educational LVS comparator, rule expansion |

---

## Why This Project Matters

This project demonstrates practical skills used in physical design and
physical verification roles:

- **Reading process design rules** — mapping SKY130 PDK specs to concrete width,
  spacing, enclosure, and area checks
- **Writing DRC rule decks** — authoring KLayout `.lydrc` scripts with
  `source()`, `report()`, `input()`, `.width()`, `.space()`, `.enclosing()`,
  and `.with_area()` APIs
- **Mapping GDS layers to rule checks** — associating SKY130 layer/datatype
  pairs (e.g. `67/20` for li1, `64/20` for nwell) with physical verification
  constraints
- **Running KLayout in batch mode** — automating DRC execution headlessly via
  Python and TCL wrappers
- **Parsing violation databases** — extracting categories, violation counts,
  and coordinates from KLayout's XML report format
- **Generating human-readable reports** — producing HTML dashboards with summary
  tables, bar charts, and per-violation detail for PV debug
- **Automating checks in CI** — running syntax checks, LVS smoke tests, and
  manifest validation on every push via GitHub Actions
- **Documenting physical verification results** — presenting DRC outcomes with
  professional rule-ID naming conventions used in real PV debug workflows

---

## Physical Verification Flow

```
  GDS Layout (layout.gds)
         │
         ▼
  KLayout Batch DRC  (klayout -b -r drc_rules.lydrc)
         │
         ▼
  Custom SKY130-style Rule Deck
  ┌──────────────────────────────────────────┐
  │  width · spacing · enclosure · area      │
  │  checks on li1, nwell, nsdm, mcon, ...   │
  └──────────────────────────────────────────┘
         │
         ▼
  XML / RDB Violation Report (results.xml)
         │
         ▼
  Python Parser (analyze_results.py)
         │
         ▼
  Summary Table + Bar Chart + HTML Dashboard
         │
         ▼
  CI Artifact / Debug Evidence
```

---

## What the Core Flow Does

1. Loads `layout.gds` — a real SKY130 `sky130_fd_sc_hd` standard-cell GDS.
2. Runs `drc_rules.lydrc` in KLayout batch mode.
3. Checks **width**, **spacing**, **enclosure**, and **area** rules against
   SKY130-style layer definitions.
4. Writes `results.xml` — the KLayout report database with all violations.
5. Parses the XML with `analyze_results.py`.
6. Generates:
   - Terminal summary table
   - Violation bar chart (`violations.png`)
   - Self-contained HTML dashboard (`drc_report.html`)

---

## DRC Rules Implemented

### Core Rules (`drc_rules.lydrc`)

| Rule ID      | Layer(s)                 | Check            | Limit        | Purpose                                          | Sample Result |
|--------------|--------------------------|------------------|--------------|--------------------------------------------------|---------------|
| `LI.W.1`    | li1 `67/20`              | Minimum width    | 0.17 µm      | Local interconnect minimum wire width            | PASS (0)      |
| `LI.S.1`    | li1 `67/20`              | Minimum spacing  | 0.17 µm      | Local interconnect minimum spacing               | PASS (0)      |
| `NW.ENC.1`  | nwell `64/20` + nsdm `93/44` | Enclosure    | 0.125 µm     | N-well enclosure of n+ source/drain implant      | PASS (0)      |
| `MCON.A.1`  | mcon `67/44`             | Minimum area     | 0.2025 µm²   | Metal contact minimum polygon area               | FAIL (18)     |

### Extended Rules (`advanced/rules/sky130_extra_rules.lydrc`)

| Rule ID      | Layer(s)                 | Check            | Limit        | Purpose                                          |
|--------------|--------------------------|------------------|--------------|--------------------------------------------------|
| `M1.W.1`    | met1 `68/20`             | Minimum width    | 0.14 µm      | Metal-1 wire width floor (lithography limit)     |
| `M1.S.1`    | met1 `68/20`             | Minimum spacing  | 0.14 µm      | Metal-1 spacing floor (short prevention)         |
| `POLY.W.1`  | poly `66/20`             | Minimum width    | 0.15 µm      | Poly gate minimum width (channel-length floor)   |
| `POLY.S.1`  | poly `66/20`             | Minimum spacing  | 0.21 µm      | Poly spacing (capacitive coupling prevention)    |
| `VIA.ENC.1` | met1 over mcon `67/44`   | Enclosure        | 0.03 µm      | Metal-1 cap over contact landing                 |
| `NW.S.1`    | nwell `64/20`            | Minimum spacing  | 1.27 µm      | N-well spacing (latch-up prevention)             |

> **Note** — Rule values are educational and reflect the spirit of the SKY130
> PDK. See `advanced/rules/rule_manifest.json` for explicit source notes per
> rule. These are not tapeout-certified values.

---

## Sample Result Summary

The following results are from running the core 4-rule deck on `layout.gds`
(cell `sky130_fd_sc_hd__a2111o_1`):

| Metric                | Result   |
|------------------------|----------|
| Total rules checked    | 4        |
| Rules passing          | 3        |
| Rules failing          | 1        |
| Total violations       | 18       |

| Rule        | Description                                   | Violations | Status |
|-------------|-----------------------------------------------|------------|--------|
| `LI.W.1`   | li1 minimum width < 0.17 µm                   | 0          | PASS   |
| `LI.S.1`   | li1 minimum spacing < 0.17 µm                 | 0          | PASS   |
| `NW.ENC.1` | nwell enclosure of nsdm < 0.125 µm            | 0          | PASS   |
| `MCON.A.1` | mcon minimum area < 0.2025 µm²                | 18         | FAIL   |

---

## Screenshots

### SKY130 Layout in KLayout

![KLayout layout view](docs/images/klayout_layout.png)

### DRC Flow Running from Terminal

![Terminal DRC run](docs/images/terminal_run.png)

### Generated HTML DRC Dashboard

![HTML DRC report](docs/images/html_report.png)

### Violation Bar Chart

![Violation chart](docs/images/violations_chart.png)

---

## KLayout Rule Deck Architecture

The DRC rule deck (`drc_rules.lydrc`) follows KLayout's batch-mode scripting API:

```ruby
# Load the GDS layout ($input is set via: klayout -rd input=layout.gds)
source($input)

# Create the report database ($output is set via: klayout -rd output=results.xml)
report("SKY130 DRC Report", $output)

# Map SKY130 GDS layers to named variables
li1   = input(67, 20)   # local interconnect
nwell = input(64, 20)   # n-well
nsdm  = input(93, 44)   # n+ source/drain implant
mcon  = input(67, 44)   # metal contact

# Run checks and store violations by rule ID
li1.width(0.17.um).output("LI.W.1", "li1 minimum width < 0.17 um")
li1.space(0.17.um).output("LI.S.1", "li1 minimum spacing < 0.17 um")
nwell.enclosing(nsdm, 0.125.um).output("NW.ENC.1", "nwell enclosure of nsdm < 0.125 um")
mcon.with_area(0.0, 0.2025).output("MCON.A.1", "mcon area < 0.2025 um^2")
```

**Key concepts:**

| API call                         | Purpose                                          |
|----------------------------------|--------------------------------------------------|
| `source($input)`                 | Loads the GDS file to check                      |
| `report(title, $output)`         | Creates the XML report database                  |
| `input(layer, datatype)`         | Maps a GDS layer/datatype pair to a layer object |
| `.width(limit)`                  | Checks minimum wire width                        |
| `.space(limit)`                  | Checks minimum spacing between shapes            |
| `.enclosing(other, limit)`       | Checks enclosure of one layer by another         |
| `.with_area(min, max)`           | Selects polygons by area range                   |
| `.output(rule_id, description)`  | Stores violations under a named rule category    |

---

## Python Automation Architecture

### `run_drc.py` — DRC Launcher

- Validates input GDS and rule-deck paths
- Locates the KLayout executable on PATH or via `--klayout`
- Launches KLayout in batch mode with `-b -r` and `-rd` variable passing
- Optionally chains `analyze_results.py` for end-to-end automation
- Returns meaningful error codes for CI integration

### `analyze_results.py` — Result Parser & Dashboard Generator

- Parses `<categories>` and `<items>` from the KLayout XML report
- Extracts rule IDs, descriptions, violation counts, and coordinates
- Generates a color-coded bar chart (`violations.png`) using matplotlib
- Writes a self-contained HTML dashboard (`drc_report.html`) using Jinja2
- Prints a terminal summary table using tabulate and pandas

---

## How to Run

### Setup

```bash
python -m pip install -r requirements.txt
```

### Run DRC + Generate Report (one command)

```bash
# Linux / macOS / WSL
python run_drc.py --input layout.gds --output results.xml --analyze

# Windows PowerShell (specify KLayout path if not on PATH)
python run_drc.py --klayout "C:\path\to\klayout_app.exe" --input layout.gds --output results.xml --analyze
```

### Run DRC Only (without report)

```bash
python run_drc.py --input layout.gds --output results.xml
```

### Run Analyzer Separately

```bash
python analyze_results.py --input results.xml --html drc_report.html
```

### Run via TCL

```bash
tclsh run_drc.tcl
```

### Run the Extended Rule Deck

```bash
python run_drc.py --rules advanced/rules/sky130_extra_rules.lydrc \
                  --input layout.gds \
                  --output results_extra.xml \
                  --analyze
```

---

## Repository Structure

```
sky130-drc-automation/
├── layout.gds                          # SKY130 standard-cell GDS input
├── drc_rules.lydrc                     # Core KLayout DRC rule deck (4 rules)
├── drc_rules.drc                       # Alternate DRC deck format
├── run_drc.py                          # Python DRC launcher (batch mode)
├── analyze_results.py                  # XML parser + HTML dashboard generator
├── run_drc.tcl                         # TCL batch automation script
├── requirements.txt                    # Python dependencies
├── results.xml                         # Sample KLayout DRC output (committed)
├── drc_report.html                     # Sample generated HTML report
├── violations.png                      # Sample generated bar chart
│
├── docs/
│   ├── images/                         # Screenshots (layout, terminal, report, chart)
│   ├── sample_drc_report.html          # Archival copy of the generated report
│   ├── ADVANCED_FLOW.md                # RTL → GDSII → DRC narrative
│   ├── CI_PIPELINE.md                  # CI workflow documentation
│   ├── LVS_DEMO.md                    # LVS conceptual walkthrough
│   └── RULE_EXPANSION.md              # Extended rule documentation
│
├── advanced/
│   ├── openlane/                       # RTL-to-GDSII OpenLane demo
│   │   ├── src/adder4.v                #   4-bit adder Verilog source
│   │   ├── config.json                 #   OpenLane config (sky130_fd_sc_hd)
│   │   └── README.md
│   ├── lvs/                            # Educational LVS comparator
│   │   ├── lvs_compare.py              #   Resistor-netlist LVS checker
│   │   ├── resistor_network.spice      #   "Schematic" netlist
│   │   ├── resistor_network_extracted.spice  # "Extracted" netlist
│   │   └── README.md
│   ├── rules/                          # Expanded DRC rules
│   │   ├── sky130_extra_rules.lydrc    #   6 additional SKY130-style rules
│   │   ├── rule_manifest.json          #   Machine-readable rule manifest
│   │   └── README.md
│   └── ci/                             # CI helper notes
│       └── README.md
│
└── .github/workflows/
    └── drc-ci.yml                      # GitHub Actions CI pipeline
```

---

## Advanced Extensions

These extensions build on top of the core DRC flow. Everything lives under
`advanced/` and `docs/` — the core flow is unchanged.

### RTL-to-GDSII OpenLane Demo

A 4-bit adder in [`advanced/openlane/src/adder4.v`](advanced/openlane/src/adder4.v)
plus an OpenLane [`config.json`](advanced/openlane/config.json) targeting
`sky130_fd_sc_hd`. Walks RTL → synthesis → P&R → GDSII, after which the
generated GDS feeds the same DRC flow. See
[`docs/ADVANCED_FLOW.md`](docs/ADVANCED_FLOW.md).

```
Verilog RTL  ──►  OpenLane (synthesis + P&R)  ──►  GDSII  ──►  KLayout DRC  ──►  HTML Report
```

> OpenLane is **not required** to use the rest of the project — it demonstrates
> how the full RTL-to-verified-layout loop works.

### Educational LVS Demo

A miniature Layout-Versus-Schematic comparator that takes two resistor-only
SPICE netlists and reports PASS / FAIL on devices, values, and connectivity.
See [`docs/LVS_DEMO.md`](docs/LVS_DEMO.md).

```bash
# PASS — netlists are equivalent
python advanced/lvs/lvs_compare.py \
       advanced/lvs/resistor_network.spice \
       advanced/lvs/resistor_network_extracted.spice

# FAIL — inject a 10% mismatch to prove the checker works
python advanced/lvs/lvs_compare.py \
       advanced/lvs/resistor_network.spice \
       advanced/lvs/resistor_network_extracted.spice \
       --inject-mismatch
```

### Expanded SKY130-Style DRC Rules

Six additional rules covering metal-1, poly, mcon enclosure, and nwell spacing,
with a JSON manifest documenting every value's source. See
[`docs/RULE_EXPANSION.md`](docs/RULE_EXPANSION.md).

### GitHub Actions CI

[`.github/workflows/drc-ci.yml`](.github/workflows/drc-ci.yml) runs on every
push and pull request:

| Step | What it checks                                                    |
|------|-------------------------------------------------------------------|
| 1    | Syntax-checks all Python sources with `py_compile`                |
| 2    | Runs LVS demo in PASS mode — confirms comparator returns 0       |
| 3    | Runs LVS demo with `--inject-mismatch` — confirms non-zero exit  |
| 4    | Validates `rule_manifest.json` is well-formed JSON                |
| 5    | Smoke-tests `analyze_results.py` on committed `results.xml`      |
| 6    | Uploads generated reports as downloadable CI artifacts            |

> KLayout itself is not installed in CI. See
> [`docs/CI_PIPELINE.md`](docs/CI_PIPELINE.md) for how to add it via a
> container image.

---

## What This Project Is Not

This project is **not**:

- A production signoff DRC deck — real SKY130 signoff decks have hundreds of
  rules, including density, antenna, and conditional spacing checks.
- A replacement for Calibre, Pegasus, ICV, or the official SKY130 DRC flow.
- A complete PDK — it uses selected SKY130 layers and educational rule values.

It **is** a working demonstration of the DRC automation loop that PV engineers
use daily: write rules → run checks → parse results → fix violations → re-run.

---

## Tool Stack

| Tool          | Purpose                                    |
|---------------|--------------------------------------------|
| KLayout       | Layout viewer and DRC engine (batch mode)  |
| Python        | DRC launcher, XML parser, report generator |
| TCL           | Optional batch automation script           |
| SKY130 PDK    | Open-source 130 nm process layer data      |
| matplotlib    | Violation bar chart generation             |
| Jinja2        | HTML dashboard templating                  |
| pandas        | Tabular result aggregation                 |
| GitHub Actions | CI smoke testing and artifact uploads     |
