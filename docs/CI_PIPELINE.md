# CI Pipeline

The CI workflow lives at
[`.github/workflows/drc-ci.yml`](../.github/workflows/drc-ci.yml) and
runs on every push and pull request to `main`. It also supports manual
runs via *Actions → drc-ci → Run workflow*.

## What the workflow checks

| Step | What it does | Why it matters |
| --- | --- | --- |
| 1 | Set up Python 3.11 | Keep CI deterministic, with pip cache for speed. |
| 2 | `pip install -r requirements.txt` | Same dependency set as a local checkout. |
| 3 | `python -m py_compile` on `run_drc.py`, `analyze_results.py`, `advanced/lvs/lvs_compare.py` | Catches syntax errors instantly, before any logic runs. |
| 4 | LVS demo, PASS path | Confirms the comparator returns 0 on equivalent netlists. |
| 5 | LVS demo with `--inject-mismatch` | Confirms the comparator returns non-zero when a real diff is present — proves the check actually works. |
| 6 | `json.load(rule_manifest.json)` | Catches accidental JSON typos in the rule manifest. |
| 7 | `analyze_results.py` on a sample `results.xml` (only if one is committed) | Smoke-tests the XML parser end-to-end. |
| 8 | Upload reports as artifacts | Lets reviewers download the generated HTML/PNG without re-running locally. |

## Why KLayout DRC is skipped in CI

KLayout is not installed on `ubuntu-latest`, and pulling it in via apt or
a release tarball significantly slows down the workflow. For a small
educational repo, this trade-off is reasonable: the CI's job here is to
keep the **Python tooling** healthy. The actual DRC step is meant to be
run locally where KLayout is already installed.

If you want to remove that limitation, two paths work well:

1. **Container-based runner.** Use a Docker image that already ships
   KLayout, e.g.

   ```yaml
   jobs:
     drc:
       runs-on: ubuntu-latest
       container:
         image: efabless/openlane:current      # ships KLayout + tools
       steps:
         - uses: actions/checkout@v4
         - run: klayout -b -r drc_rules.lydrc \
                        -rd input=layout.gds \
                        -rd output=results.xml
         - run: python analyze_results.py --input results.xml
   ```

2. **Self-hosted runner.** Useful if your repo grows large GDSII files;
   you keep them off GitHub-hosted runners.

## Adding a README badge

Once the workflow has run at least once, you can drop this near the top
of `README.md` (replace `<owner>` if you ever fork):

```markdown
![drc-ci](https://github.com/abdo-ehab-euv/sky130-drc-automation/actions/workflows/drc-ci.yml/badge.svg)
```

## Extending later

- Run the `advanced/rules/sky130_extra_rules.lydrc` deck once KLayout is
  available in CI and upload the second HTML report as an artifact.
- Add a step that fails the build if the violation count regresses
  beyond a threshold — closing the loop into "DRC as a CI gate".
- Cache the SKY130 PDK if you use OpenLane in CI (the PDK download is
  the slowest step of an OpenLane run).
