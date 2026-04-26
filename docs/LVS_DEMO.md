# LVS Demo

## What LVS means

**LVS** stands for *Layout-Versus-Schematic*. After your layout passes
DRC (i.e. it can be manufactured), LVS asks the next obvious question:

> "Does this layout actually implement the circuit I designed?"

Concretely, an LVS engine does three things:

1. **Extracts** a netlist from the layout — recognising the polygons as
   transistors, resistors, capacitors, and the metal/poly shapes
   connecting them.
2. **Reads** the schematic netlist (the SPICE produced by the schematic
   editor or synthesised RTL).
3. **Compares** the two netlists and reports whether they describe the
   same circuit.

If LVS fails, the chip will likely tape out as a layout that doesn't
match the verified schematic — so its electrical behaviour is unknown.
Tools like Calibre LVS, KLayout's netlist compare, and Magic+netgen all
do this for real designs.

## Why real LVS is harder than DRC

DRC asks one shape-by-shape question: *"is this geometry legal?"*. LVS
asks a graph-isomorphism question: *"are these two netlists the same
circuit, possibly with different instance and net names?"*.

That makes real LVS substantially harder, because it must:

- handle MOSFETs with permutable source/drain pins,
- recognise hierarchies and subcircuits across boundaries,
- tolerate parameter rounding from extraction,
- understand power and ground aliases (`VDD`, `vdd!`, `vcc`, …),
- collapse parasitic R/C added by extraction.

## How this demo maps to layout-vs-schematic thinking

This repo doesn't have a real layout extractor — we'd need a much
larger toolchain for that. Instead, we ship two **hand-written SPICE
netlists** that look like a real schematic-vs-extracted pair:

| File                                 | Role                                |
|--------------------------------------|-------------------------------------|
| `resistor_network.spice`             | The "schematic"                     |
| `resistor_network_extracted.spice`   | The "layout-extracted" copy         |

Both describe the same divider:

```
VIN ──[ R = 1 kΩ ]── VOUT ──[ R = 2 kΩ ]── VSS
```

The instance names differ (`R1`/`R2` vs `Rx_extracted_1`/
`Rx_extracted_2`) — exactly the kind of divergence a real extraction
tool produces. `lvs_compare.py` parses both, builds a canonical
device set keyed on (terminals, value), and confirms they match.

## How to run

```bash
# PASS — the two files describe the same circuit.
python advanced/lvs/lvs_compare.py \
       advanced/lvs/resistor_network.spice \
       advanced/lvs/resistor_network_extracted.spice

# FAIL — bump the first resistor in memory by 10% to demonstrate
# that the comparator actually catches differences.
python advanced/lvs/lvs_compare.py \
       advanced/lvs/resistor_network.spice \
       advanced/lvs/resistor_network_extracted.spice \
       --inject-mismatch
```

## Example PASS output

```
=== LVS Compare ===
  Schematic : advanced/lvs/resistor_network.spice
  Extracted : advanced/lvs/resistor_network_extracted.spice

  Schematic devices : 2
  Extracted devices : 2

RESULT: PASS — netlists are equivalent (devices, values, and connectivity all match).
```

## Example FAIL output (with `--inject-mismatch`)

```
=== LVS Compare ===
  Schematic : advanced/lvs/resistor_network.spice
  Extracted : advanced/lvs/resistor_network_extracted.spice
  Mode      : --inject-mismatch (intentional FAIL)

  Schematic devices : 2
  Extracted devices : 2

RESULT: FAIL — netlists differ. Details:
  Devices only in SCHEMATIC:
     x1  R between VIN <-> VOUT, value = 1000.0 Ω
  Devices only in EXTRACTED:
     x1  R between VIN <-> VOUT, value = 1100.0 Ω
```

The actual numbers may differ slightly when you run it.

## Suggested next steps

- Add a **MOSFET** version: parse `M*` lines, recognise S/D
  permutability, and compare a tiny inverter schematic against an
  extracted netlist.
- Wire in **KLayout's** built-in netlist compare (it ships an LVS API in
  Ruby/Python) for a real, layout-driven LVS instead of this hand-rolled
  one.
- Add a `--tolerance` flag so resistor values can match within a
  configurable percent.
