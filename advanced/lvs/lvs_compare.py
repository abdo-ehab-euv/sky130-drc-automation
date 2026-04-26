#!/usr/bin/env python3
"""
lvs_compare.py
==============

A tiny educational LVS (Layout-Versus-Schematic) checker for resistor-only
SPICE netlists.

It parses two SPICE files, builds a canonical representation of each
network, and prints PASS or FAIL with a clear diff if the two are not
equivalent.

Usage
-----
    python lvs_compare.py schematic.spice extracted.spice
    python lvs_compare.py schematic.spice extracted.spice --inject-mismatch

The --inject-mismatch flag tampers with the extracted netlist *in memory*
to demonstrate that the comparator catches real differences. It does NOT
modify the file on disk.

What this is, and what it isn't
-------------------------------
* This is an educational demo. Real LVS engines (Calibre, KLayout's
  netlist compare, magic+netgen) handle MOSFETs, hierarchies, parameter
  tolerances, port permutations, and net-name aliasing. We do none of
  that here.
* What we DO show: parsing devices, normalizing nets, and checking that
  two netlists describe the same circuit topology.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Resistor:
    """One resistor instance: which two nets it touches and its value (Ω)."""
    net_a: str
    net_b: str
    value_ohms: float

    def canonical(self) -> Tuple[str, str, float]:
        """
        Return a tuple that's invariant to terminal order. A resistor between
        (VIN, VOUT, 1000) and (VOUT, VIN, 1000) is the same device, so we
        sort the two terminals before comparing.
        """
        a, b = sorted([self.net_a, self.net_b])
        return (a, b, float(self.value_ohms))


# ---------------------------------------------------------------------------
# SPICE parsing (resistor-only subset)
# ---------------------------------------------------------------------------

def parse_value(token: str) -> float:
    """
    Parse a SPICE-style resistance value. Supports the common SI suffixes
    (k, meg, m, u, n, p) but we only really need 'k' for this demo.
    """
    suffixes = {
        "t":   1e12,
        "g":   1e9,
        "meg": 1e6,
        "k":   1e3,
        "m":   1e-3,
        "u":   1e-6,
        "n":   1e-9,
        "p":   1e-12,
    }
    s = token.strip().lower()
    # Try plain float first.
    try:
        return float(s)
    except ValueError:
        pass
    # Then try suffix forms ('1k', '2.2k', '1meg').
    for suffix, mult in sorted(suffixes.items(), key=lambda kv: -len(kv[0])):
        if s.endswith(suffix):
            head = s[:-len(suffix)]
            try:
                return float(head) * mult
            except ValueError:
                break
    raise ValueError(f"Could not parse resistance value: {token!r}")


def parse_netlist(path: Path) -> List[Resistor]:
    """
    Parse a tiny SPICE netlist and return the list of resistors.

    Recognized line shape: ``Rname netA netB value``
    Lines starting with ``*`` (comments), ``.`` (directives like .end), or
    blank lines are skipped.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Netlist not found: {path}")

    devices: List[Resistor] = []
    with path.open("r", encoding="utf-8") as f:
        for raw_line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("*") or line.startswith("."):
                continue
            tokens = line.split()
            if not tokens:
                continue
            head = tokens[0].lower()
            if head.startswith("r"):
                if len(tokens) < 4:
                    raise ValueError(
                        f"{path}:{raw_line_no}: malformed resistor line: {raw!r}")
                _name, net_a, net_b, val = tokens[0], tokens[1], tokens[2], tokens[3]
                devices.append(Resistor(net_a=net_a, net_b=net_b,
                                        value_ohms=parse_value(val)))
            else:
                # Quietly ignore non-resistor devices for this demo.
                # A real LVS would parse them; we just skip and tell the user.
                print(f"  note: ignoring non-resistor line "
                      f"({path.name}:{raw_line_no}): {line}")
    return devices


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def device_multiset(devices: List[Resistor]) -> Counter:
    """Multiset of canonical resistor tuples — order-independent comparison."""
    return Counter(d.canonical() for d in devices)


def net_multiset(devices: List[Resistor]) -> Counter:
    """How many device terminals touch each net."""
    counter: Counter = Counter()
    for d in devices:
        counter[d.net_a] += 1
        counter[d.net_b] += 1
    return counter


def compare(schem: List[Resistor], extr: List[Resistor]) -> Tuple[bool, List[str]]:
    """
    Return (is_equivalent, list_of_messages).

    The comparison is name-insensitive but value- and connectivity-sensitive,
    which is the right default for LVS thinking: the *circuit* must match,
    not the instance names.
    """
    msgs: List[str] = []

    if len(schem) != len(extr):
        msgs.append(f"Device count mismatch: schematic has {len(schem)}, "
                    f"extracted has {len(extr)}.")

    s_devs = device_multiset(schem)
    e_devs = device_multiset(extr)

    if s_devs != e_devs:
        only_schem = s_devs - e_devs
        only_extr  = e_devs - s_devs
        if only_schem:
            msgs.append("Devices only in SCHEMATIC:")
            for (a, b, v), n in only_schem.items():
                msgs.append(f"   x{n}  R between {a} <-> {b}, value = {v} Ω")
        if only_extr:
            msgs.append("Devices only in EXTRACTED:")
            for (a, b, v), n in only_extr.items():
                msgs.append(f"   x{n}  R between {a} <-> {b}, value = {v} Ω")

    s_nets = net_multiset(schem)
    e_nets = net_multiset(extr)
    if s_nets != e_nets:
        all_nets = sorted(set(s_nets) | set(e_nets))
        msgs.append("Net connectivity mismatch (terminal counts per net):")
        msgs.append(f"   {'Net':<10}  {'Schem':>6}  {'Extr':>6}")
        for net in all_nets:
            s = s_nets.get(net, 0)
            e = e_nets.get(net, 0)
            mark = "" if s == e else "  <-- DIFF"
            msgs.append(f"   {net:<10}  {s:>6}  {e:>6}{mark}")

    return (len(msgs) == 0), msgs


# ---------------------------------------------------------------------------
# Mismatch injection (for demo / testing)
# ---------------------------------------------------------------------------

def inject_mismatch(devices: List[Resistor]) -> List[Resistor]:
    """
    Return a tampered copy of the device list that is no longer equivalent
    to the schematic. We change the value of the first resistor by 10%,
    which is enough to fail value-aware LVS but not so much that the diff
    becomes confusing.
    """
    if not devices:
        return devices
    head, *tail = devices
    bumped = Resistor(net_a=head.net_a, net_b=head.net_b,
                      value_ohms=head.value_ohms * 1.10)
    return [bumped] + tail


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Tiny educational LVS comparator for resistor SPICE netlists.")
    p.add_argument("schematic", type=Path, help="Schematic SPICE netlist")
    p.add_argument("extracted", type=Path, help="Layout-extracted SPICE netlist")
    p.add_argument("--inject-mismatch", action="store_true",
                   help="Tamper with the extracted netlist in memory to "
                        "demonstrate a FAIL result (does not modify any file).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    print("=== LVS Compare ===")
    print(f"  Schematic : {args.schematic}")
    print(f"  Extracted : {args.extracted}")
    if args.inject_mismatch:
        print("  Mode      : --inject-mismatch (intentional FAIL)")
    print()

    try:
        schem = parse_netlist(args.schematic)
        extr  = parse_netlist(args.extracted)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"  Schematic devices : {len(schem)}")
    print(f"  Extracted devices : {len(extr)}")
    print()

    if args.inject_mismatch:
        extr = inject_mismatch(extr)

    ok, messages = compare(schem, extr)

    if ok:
        print("RESULT: PASS — netlists are equivalent (devices, values, "
              "and connectivity all match).")
        return 0

    print("RESULT: FAIL — netlists differ. Details:")
    for m in messages:
        print(f"  {m}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
