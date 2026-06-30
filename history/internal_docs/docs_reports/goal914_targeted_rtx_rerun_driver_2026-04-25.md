# Goal 914 Targeted RTX Rerun Driver

Date: 2026-04-25

## Purpose

Goal913 fixed the local graph visibility gate shape and added Jaccard candidate
diagnostics, but the RTX pod is currently unreachable. Goal914 adds a small
driver for the next pod session so we do not spend cloud time on the full suite
when only Group F graph and Group H Jaccard require follow-up.

## Added Script

`scripts/goal914_rtx_targeted_graph_jaccard_rerun.py`

Default dry run:

```bash
PYTHONPATH=src:. python3 scripts/goal914_rtx_targeted_graph_jaccard_rerun.py \
  --mode dry-run \
  --output-json docs/reports/goal914_rtx_targeted_graph_jaccard_rerun.json
```

Cloud run:

```bash
PYTHONPATH=src:. python3 scripts/goal914_rtx_targeted_graph_jaccard_rerun.py \
  --mode run \
  --copies 20000 \
  --graph-chunk-copies 100 \
  --jaccard-chunk-copies 100,50,20 \
  --output-json docs/reports/goal914_rtx_targeted_graph_jaccard_rerun_rtx.json
```

## Behavior

- Runs the fixed Goal889 graph gate once with strict summary/analytic validation.
- Runs the Jaccard production shape first at `--chunk-copies 100`.
- If needed, also records smaller Jaccard diagnostic chunk sizes (`50`, `20`) in
  the same pod session.
- Avoids the full cloud suite and makes no RTX speedup claim.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal914_rtx_targeted_graph_jaccard_rerun_test -v
```

Result: 2 tests OK.

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal914_rtx_targeted_graph_jaccard_rerun.py \
  tests/goal914_rtx_targeted_graph_jaccard_rerun_test.py
```

Result: passed.
