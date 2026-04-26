# Rule Expansion: SKY130-Style DRC Rules

This document explains the **6 additional DRC rules** in
`advanced/rules/sky130_extra_rules.lydrc`, why they are useful as a
learning step, and how they relate to a real foundry deck.

> ⚠️ Educational values. The numbers below capture the *spirit* of the
> SKY130 PDK but should not be treated as tapeout-certified. See
> `advanced/rules/rule_manifest.json` for explicit source notes per rule.

## Rule table

| Rule ID     | Layer(s)                  | Check             | Value (µm) | Why it exists                                                                 |
|-------------|---------------------------|-------------------|-----------:|-------------------------------------------------------------------------------|
| `M1.W.1`    | met1 (68/20)              | minimum width     | 0.14       | Below this width, lithography cannot reliably print the wire.                 |
| `M1.S.1`    | met1 (68/20)              | minimum spacing   | 0.14       | Below this spacing, two adjacent wires risk shorting after etch.              |
| `POLY.W.1`  | poly (66/20)              | minimum width     | 0.15       | Channel-length floor: a thinner gate degrades transistor behaviour.           |
| `POLY.S.1`  | poly (66/20)              | minimum spacing   | 0.21       | Two close gate strips couple capacitively and can short during silicide.      |
| `VIA.ENC.1` | met1 over mcon (67/44)    | enclosure         | 0.03       | The metal cap above the contact must be wide enough to land on it reliably.   |
| `NW.S.1`    | nwell (64/20)             | minimum spacing   | 1.27       | Latch-up: two close nwells can form a parasitic SCR and cause a chip lock-up. |

## How to run the extra rule deck

The extra deck reuses the same `-rd input` / `-rd output` convention as
the core deck, so `run_drc.py` works with no changes:

```bash
# Just the extra deck
python run_drc.py --rules advanced/rules/sky130_extra_rules.lydrc \
                  --input layout.gds \
                  --output results_extra.xml \
                  --html drc_report_extra.html \
                  --analyze
```

Or invoke KLayout directly (matches `run_drc.tcl` style):

```bash
klayout -b -r advanced/rules/sky130_extra_rules.lydrc \
        -rd input=layout.gds \
        -rd output=results_extra.xml
```

## How this differs from a real foundry deck

A production sign-off DRC deck for SKY130 contains **hundreds** of
rules, not 10. The differences boil down to four things:

1. **Density / CMP rules.** Real fabs require minimum and maximum metal
   density per window so chemical-mechanical polishing produces flat
   wafers.
2. **Antenna ratio rules.** Long metal antennas can damage gate oxide
   during plasma etch. None of those checks are here.
3. **Conditional rules.** Real spacings depend on adjacent shape width
   and run length; e.g. "spacing of 0.14 µm normally, but 0.28 µm if a
   parallel run exceeds 2 µm". This deck only encodes the unconditional
   minimums.
4. **Logical operations.** Rules like *"N+ implant must overlap diff
   inside nwell"* require boolean operations between layers
   (`nsdm AND nwell`). The simple width/spacing checks here don't go
   that deep.

## Why named rule IDs matter in PV debug

A real PV team refers to violations by rule ID in chat, JIRA tickets, and
waiver files — *"the only remaining failure is `M1.S.3` in the IO
ring"*. Reproducing that pattern here (`M1.W.1`, `POLY.S.1`, …)
makes the dashboard talk like a real DRC log and trains the muscle for
"locate-fix-rerun" debugging.

When you grep for a rule ID across the rule deck, the manifest, and the
generated HTML report, everything lines up — that consistency *is* the
deliverable. A real deck has the same property: the rule ID is the
contract between the rule writer, the layout designer, and the verifier.
