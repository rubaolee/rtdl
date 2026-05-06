# Goal 1408: v1.5 vs v1.0 Performance Harness

Date: 2026-05-06

## Purpose

This goal adds a same-command performance harness for comparing the released
`v1.0` tag against the current v1.5 release candidate.

The harness does not authorize public speedup wording by itself. It records
bounded app/subpath timings and preserves each app boundary.

## Harness

Script:

```sh
python3 scripts/goal1408_v1_5_vs_v1_0_perf_runner.py
```

The script:

- creates or reuses a detached `v1.0` worktree;
- runs matching profiler commands against `v1.0` and current `main`;
- records stdout/stderr tails, selected metric path, selected metric seconds,
  and comparison ratio;
- marks unavailable/error cells explicitly instead of treating them as zero;
- writes `summary.json` and `summary.md`.

## Local Embree Smoke

Local macOS Embree smoke output:

```text
docs/reports/goal1408_v1_5_vs_v1_0_perf_local_embree/summary.json
docs/reports/goal1408_v1_5_vs_v1_0_perf_local_embree/summary.md
```

This local artifact validates harness mechanics and records a same-machine
comparison, but Linux Embree is preferred for the final v1.5-vs-v1.0 Embree
table.

## Linux Embree Next Step

Run from a clean Linux checkout:

```sh
PYTHONPATH=src:. python3 scripts/goal1408_v1_5_vs_v1_0_perf_runner.py \
  --backends embree \
  --copies 512 \
  --iterations 3 \
  --timeout-sec 240 \
  --output-dir docs/reports/goal1408_v1_5_vs_v1_0_perf_linux_embree
```

The OptiX side should be run on an NVIDIA pod from the same committed harness.

## Verification

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1408_v1_5_vs_v1_0_perf_runner_test
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal1408_v1_5_vs_v1_0_perf_runner.py \
  tests/goal1408_v1_5_vs_v1_0_perf_runner_test.py
git diff --check
```
