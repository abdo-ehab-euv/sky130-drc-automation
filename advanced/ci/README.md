# CI Pipeline

The CI workflow lives at [`.github/workflows/drc-ci.yml`](../../.github/workflows/drc-ci.yml).

This folder is intentionally tiny — it just exists so the `advanced/`
tree has a stable home for any future CI helper scripts (Dockerfiles for
a KLayout image, custom runners, etc.).

## What the CI checks today

1. Installs Python dependencies from `requirements.txt`.
2. Syntax-checks `run_drc.py`, `analyze_results.py`, and
   `advanced/lvs/lvs_compare.py` with `py_compile`.
3. Runs the LVS demo in PASS mode and confirms it exits 0.
4. Runs the LVS demo with `--inject-mismatch` and confirms it exits
   non-zero (i.e. the comparator actually detects the injected diff).
5. Validates `advanced/rules/rule_manifest.json` is well-formed JSON.
6. If a sample `results.xml` is committed, runs `analyze_results.py` on
   it as a smoke test for the parser.
7. Uploads any generated reports as a downloadable build artifact.

KLayout itself is not installed in CI — see
[`docs/CI_PIPELINE.md`](../../docs/CI_PIPELINE.md) for how to add it
later.
