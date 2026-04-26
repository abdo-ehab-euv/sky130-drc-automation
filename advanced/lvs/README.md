# Educational LVS Demo

A miniature Layout-Versus-Schematic (LVS) checker that compares two
resistor-only SPICE netlists and reports whether they describe the same
circuit.

> ⚠️ This is an **educational demo**, not a production LVS engine.
> Real LVS handles MOSFETs, hierarchies, parameter tolerances, port
> permutations, and so on. We do none of that — we just compare devices,
> values, and connectivity for resistor networks.

---

## Files

| File                                | Purpose                                        |
|-------------------------------------|------------------------------------------------|
| `resistor_network.spice`            | "Schematic" netlist                            |
| `resistor_network_extracted.spice`  | "Layout-extracted" netlist (different names)   |
| `lvs_compare.py`                    | Comparator script                              |

The two netlists are deliberately different in **instance names** but
identical in **devices, connections, and values** — exactly the pattern a
real extractor produces vs. a schematic.

## Run a clean comparison (PASS)

From the project root:

```bash
python advanced/lvs/lvs_compare.py advanced/lvs/resistor_network.spice advanced/lvs/resistor_network_extracted.spice
```

Expected output ends with:

```
RESULT: PASS — netlists are equivalent (devices, values, and connectivity all match).
```

## Force a failure to verify the checker (FAIL)

```bash
python advanced/lvs/lvs_compare.py advanced/lvs/resistor_network.spice advanced/lvs/resistor_network_extracted.spice --inject-mismatch
```

This bumps the first resistor's value by 10 % **in memory**. The on-disk
files are untouched. You'll see a FAIL with a clear diff explaining what
no longer matches.

This proves the comparator is doing real work — it isn't just printing
PASS for everything.

## Limitations

- Only resistor (`R...`) lines are parsed. Other device types are
  reported and skipped.
- No subcircuit (`.subckt`) handling.
- No port-aliasing or net-renaming logic.
- Values are compared exactly. Realistic LVS allows small tolerances on
  parasitic-extracted values.

See [`docs/LVS_DEMO.md`](../../docs/LVS_DEMO.md) for the conceptual
walkthrough.
