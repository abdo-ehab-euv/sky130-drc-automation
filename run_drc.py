#!/usr/bin/env python3
"""
run_drc.py
==========

Runs KLayout in batch mode against a GDS layout using the drc_rules.lydrc
rule deck, and optionally runs analyze_results.py afterwards.

Usage
-----
    python run_drc.py --input layout.gds --output results.xml
    python run_drc.py --input layout.gds --output results.xml --analyze

Cross-platform: works on Linux, macOS, and Windows as long as the `klayout`
executable is on PATH (or is supplied via --klayout).
"""

import argparse
import os
import shutil
import subprocess
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run KLayout DRC on a SKY130 layout and (optionally) build a report.")
    parser.add_argument("--input",   default="layout.gds",
                        help="Input GDS layout (default: layout.gds)")
    parser.add_argument("--output",  default="results.xml",
                        help="Output DRC report XML (default: results.xml)")
    parser.add_argument("--rules",   default="drc_rules.lydrc",
                        help="KLayout DRC rule deck (default: drc_rules.lydrc)")
    parser.add_argument("--klayout", default="klayout",
                        help="Path to the klayout executable (default: klayout on PATH)")
    parser.add_argument("--analyze", action="store_true",
                        help="After DRC, run analyze_results.py to build the HTML report")
    parser.add_argument("--html",    default="drc_report.html",
                        help="HTML report (only used with --analyze, default: drc_report.html)")
    return parser.parse_args()


def find_klayout(user_path):
    """
    Locate the klayout binary. Accepts an explicit path, or a name to look up
    on PATH. Returns the usable path, or None if we cannot find it.
    """
    # If the user passed an absolute/relative path that exists, use it.
    if os.path.isfile(user_path):
        return user_path
    # Otherwise search PATH (handles klayout / klayout.exe / etc.).
    found = shutil.which(user_path)
    return found


def main():
    args = parse_args()

    # --- Sanity checks on inputs ------------------------------------------
    if not os.path.isfile(args.input):
        print(f"ERROR: Input GDS file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.rules):
        print(f"ERROR: DRC rule file not found: {args.rules}", file=sys.stderr)
        sys.exit(1)

    klayout_bin = find_klayout(args.klayout)
    if klayout_bin is None:
        print(f"ERROR: Could not find KLayout executable '{args.klayout}'.",
              file=sys.stderr)
        print("       Install KLayout from https://www.klayout.de and either",
              file=sys.stderr)
        print("       add it to your PATH or pass --klayout /path/to/klayout.",
              file=sys.stderr)
        sys.exit(1)

    # --- Build the KLayout command ----------------------------------------
    # This must match the variable names ($input, $output) used in drc_rules.lydrc.
    cmd = [
        klayout_bin,
        "-b",
        "-r", args.rules,
        "-rd", f"input={args.input}",
        "-rd", f"output={args.output}",
    ]

    print("Running command:")
    print("  " + " ".join(cmd))
    print()

    # --- Execute KLayout --------------------------------------------------
    start = time.time()
    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print(f"ERROR: Failed to launch KLayout ({klayout_bin}).", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"ERROR: KLayout exited with code {result.returncode} "
              f"after {elapsed:.2f} s.", file=sys.stderr)
        print("       Re-run the command above manually to see the full log.",
              file=sys.stderr)
        sys.exit(result.returncode)

    print()
    print(f"DRC finished in {elapsed:.2f} s")
    print(f"Report written to: {args.output}")

    # --- Optional analysis step -------------------------------------------
    if args.analyze:
        # Resolve analyze_results.py relative to THIS script so it works no
        # matter what directory the user launches run_drc.py from.
        analyze_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "analyze_results.py")

        if not os.path.isfile(analyze_script):
            print(f"ERROR: analyze_results.py not found next to run_drc.py "
                  f"({analyze_script}).", file=sys.stderr)
            sys.exit(1)

        analyze_cmd = [
            sys.executable, analyze_script,
            "--input", args.output,
            "--html",  args.html,
        ]
        print()
        print("Running analyzer:")
        print("  " + " ".join(analyze_cmd))

        ret = subprocess.run(analyze_cmd).returncode
        if ret != 0:
            print(f"ERROR: analyze_results.py exited with code {ret}",
                  file=sys.stderr)
            sys.exit(ret)


if __name__ == "__main__":
    main()
