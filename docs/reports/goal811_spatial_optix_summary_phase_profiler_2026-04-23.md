# Goal811 Spatial OptiX Prepared-Summary Phase Profiler

## Result

Goal811 adds phase-clean profiler tooling for the two spatial apps promoted to OptiX prepared-summary surfaces in Goal810.

The profiler covers:

- `service_coverage_gaps`
- `event_hotspot_screening`

## What Changed

- Added `/Users/rl2025/rtdl_python_only/scripts/goal811_spatial_optix_summary_phase_profiler.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal811_spatial_optix_summary_phase_profiler_test.py`.
- Updated `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py` so service/event prepared-summary paths are listed as deferred RTX entries.
- The profiler supports `--mode dry-run` for portable local schema/reference checks.
- The profiler supports `--mode optix` for later Linux/RTX runs.
- OptiX mode separates:
  - input construction;
  - OptiX prepared scene construction;
  - prepared fixed-radius query;
  - Python summary postprocess.

## Intended RTX Commands

```bash
PYTHONPATH=src:. python3 scripts/goal811_spatial_optix_summary_phase_profiler.py \
  --scenario service_coverage_gaps \
  --mode optix \
  --copies 20000 \
  --output-json docs/reports/goal811_service_coverage_rtx.json

PYTHONPATH=src:. python3 scripts/goal811_spatial_optix_summary_phase_profiler.py \
  --scenario event_hotspot_screening \
  --mode optix \
  --copies 20000 \
  --output-json docs/reports/goal811_event_hotspot_rtx.json
```

These should be run only in a batched RTX session, not as separate pod restarts.

## Boundary

This profiler does not authorize a public speedup claim. It packages the phase evidence needed before `service_coverage_gaps` or `event_hotspot_screening` can move beyond `needs_phase_contract`.

`facility_knn_assignment` remains excluded from this goal because KNN ranking is not implemented by the fixed-radius count-threshold primitive.

## Verification

Completed:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal811_spatial_optix_summary_phase_profiler_test tests.goal810_spatial_apps_optix_summary_surface_test -v
python3 -m py_compile scripts/goal811_spatial_optix_summary_phase_profiler.py tests/goal811_spatial_optix_summary_phase_profiler_test.py
git diff --check
```

Result: 33 tests OK, `py_compile` OK, and `git diff --check` OK.

Portable dry-runs completed:

```bash
PYTHONPATH=src:. python3 scripts/goal811_spatial_optix_summary_phase_profiler.py \
  --scenario service_coverage_gaps \
  --mode dry-run \
  --copies 4 \
  --output-json docs/reports/goal811_service_coverage_dry_run_2026-04-23.json

PYTHONPATH=src:. python3 scripts/goal811_spatial_optix_summary_phase_profiler.py \
  --scenario event_hotspot_screening \
  --mode dry-run \
  --copies 4 \
  --output-json docs/reports/goal811_event_hotspot_dry_run_2026-04-23.json
```
