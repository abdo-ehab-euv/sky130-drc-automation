# Expanded SKY130-Style DRC Rules

This folder adds **6 extra DRC rules** on top of the 4 core rules in the
project root deck. The new rules cover **metal1**, **poly**, **mcon
enclosure**, and **nwell spacing** — common families a PV engineer
debugs first.

> ⚠️ Values here are **educational**. They reflect the spirit of the
> SKY130 PDK but should not be treated as tapeout-certified. The
> `rule_manifest.json` file documents each value and where to verify it.

---

## Files

| File                         | Purpose                                            |
|------------------------------|----------------------------------------------------|
| `sky130_extra_rules.lydrc`   | KLayout DRC deck with the 6 extra rules            |
| `rule_manifest.json`         | Machine-readable list of every rule + source notes |

## Rules

| Rule ID     | Layer(s)                  | Check             | Value (µm) |
|-------------|---------------------------|-------------------|-----------:|
| `M1.W.1`    | met1 (68/20)              | minimum width     | 0.14       |
| `M1.S.1`    | met1 (68/20)              | minimum spacing   | 0.14       |
| `POLY.W.1`  | poly (66/20)              | minimum width     | 0.15       |
| `POLY.S.1`  | poly (66/20)              | minimum spacing   | 0.21       |
| `VIA.ENC.1` | met1 over mcon (67/44)    | enclosure         | 0.03       |
| `NW.S.1`    | nwell (64/20)             | minimum spacing   | 1.27       |

## How to run the extra rule deck

The extra deck uses the same `-rd input=... -rd output=...` convention as
the core deck. From the project root:

```powershell
# Windows PowerShell
klayout -b -r advanced\rules\sky130_extra_rules.lydrc `
        -rd input=layout.gds `
        -rd output=results_extra.xml
```

```bash
# macOS / Linux / WSL
klayout -b -r advanced/rules/sky130_extra_rules.lydrc \
        -rd input=layout.gds \
        -rd output=results_extra.xml
```

You can also feed the result to the existing analyzer:

```bash
python analyze_results.py --input results_extra.xml \
                          --html  drc_report_extra.html \
                          --chart violations_extra.png
```

Or do everything in one shot via `run_drc.py`:

```bash
python run_drc.py --rules advanced/rules/sky130_extra_rules.lydrc \
                  --input layout.gds \
                  --output results_extra.xml \
                  --html drc_report_extra.html \
                  --analyze
```

## How this differs from a real foundry deck

A production SKY130 sign-off DRC deck has hundreds of rules with
context-sensitive checks (e.g. spacing varies with run length, width,
density). It also includes:

- antenna ratio checks
- density (CMP) checks
- N+/P+ implant rules with logical operations
- well-tap distance enforcement
- latch-up rules with deep-nwell awareness

This deck has six geometric checks. It's designed to be **readable** so a
reader can match each line to a physical concept, not to be exhaustive.

## Why named rule IDs matter in PV debug

Real PV teams refer to violations by their rule ID in chat, JIRA tickets,
and waiver files (e.g. *"the only remaining failure is M1.S.3 in the IO
ring"*). Reproducing that pattern here — `M1.W.1`, `POLY.S.1`, etc. —
makes the dashboard talk like a real DRC log and trains the muscle for
"locate-fix-rerun" debugging.

See [`docs/RULE_EXPANSION.md`](../../docs/RULE_EXPANSION.md) for the
narrative version.
