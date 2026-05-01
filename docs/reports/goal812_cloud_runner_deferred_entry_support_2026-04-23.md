# Goal812 Cloud Runner Deferred Entry Support

## Result

Goal812 updates the manifest-driven RTX cloud runner so deferred readiness gates can be included deliberately in a batched cloud session.

## What Changed

- `/Users/rl2025/rtdl_python_only/scripts/goal761_rtx_cloud_run_all.py` now accepts `--include-deferred`.
- `run_all(...)` now accepts `include_deferred=True`.
- Runner output records `include_deferred` and per-result `manifest_section`.
- Deferred entries remain excluded by default.

## Why

Goals807 and 811 added deferred gates for segment/polygon and spatial prepared-summary apps. Without explicit runner support, those gates would require manual cloud commands. With `--include-deferred`, a future paid RTX pod can run active entries and selected deferred readiness gates in one controlled batch.

## Example

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only service_coverage_gaps \
  --only event_hotspot_screening \
  --only segment_polygon_hitcount \
  --output-json docs/reports/goal812_deferred_spatial_segpoly_rtx.json
```

## Boundary

Including deferred entries does not promote them to claim status. It only runs readiness gates. Public RTX claims still require successful cloud artifacts, phase-clean analysis, and independent review.

## Verification

Completed:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal761_rtx_cloud_run_all_test tests.goal759_rtx_cloud_benchmark_manifest_test -v
python3 -m py_compile scripts/goal761_rtx_cloud_run_all.py
git diff --check
```

Result: 12 tests OK, `py_compile` OK, and `git diff --check` OK.

Deferred-entry dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --include-deferred \
  --only service_coverage_gaps \
  --only event_hotspot_screening \
  --only segment_polygon_hitcount \
  --output-json docs/reports/goal812_deferred_spatial_segpoly_dry_run_2026-04-23.json
```

Result: 3 deferred entries selected, 3 unique commands, all `dry_run`.
