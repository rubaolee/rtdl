# Goal1037 Local Baseline Manifest SciPy Wording Sync

Date: 2026-04-26

## Scope

Goal1037 fixes stale wording in the Goal1030 local baseline manifest. After Goal1034 created `.venv-rtdl-scipy` and verified SciPy command health, the manifest still said this Mac lacked SciPy for the four `baseline_ready` apps.

## Change

Updated `scripts/goal1030_local_baseline_manifest.py` so the four SciPy-capable `baseline_ready` rows state:

- SciPy remains an optional dependency.
- SciPy is available locally through the project venv used by Goal1034+.

Regenerated:

- `docs/reports/goal1030_local_baseline_manifest_2026-04-26.json`
- `docs/reports/goal1030_local_baseline_manifest_2026-04-26.md`

## Validation

```bash
PYTHONPATH=src:. python3 scripts/goal1030_local_baseline_manifest.py \
  --output-json docs/reports/goal1030_local_baseline_manifest_2026-04-26.json \
  --output-md docs/reports/goal1030_local_baseline_manifest_2026-04-26.md

PYTHONPATH=src:. python3 -m unittest \
  tests/goal1030_local_baseline_manifest_test.py \
  tests/goal1031_local_baseline_smoke_runner_test.py
```

Result: `7 tests OK`.

## Boundary

This is a documentation/manufactured-artifact sync only. It does not change readiness counts, execute new benchmarks, authorize public speedup claims, or authorize release.
