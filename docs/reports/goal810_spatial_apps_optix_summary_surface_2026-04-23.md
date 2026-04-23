# Goal810 Spatial Apps OptiX Prepared Summary Surface

## Result

Goal810 adds bounded OptiX prepared-summary surfaces to two spatial apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

These surfaces use the existing prepared fixed-radius count-threshold OptiX traversal primitive. They avoid neighbor-row materialization when the app only needs coverage or hotspot summaries.

## What Changed

- `/Users/rl2025/rtdl_python_only/examples/rtdl_service_coverage_gaps.py`
  - Adds `--backend optix`.
  - Adds `--optix-summary-mode rows|gap_summary_prepared`.
  - `gap_summary_prepared` prepares the clinic point set and emits covered/uncovered household summary evidence.
- `/Users/rl2025/rtdl_python_only/examples/rtdl_event_hotspot_screening.py`
  - Adds `--backend optix`.
  - Adds `--optix-summary-mode rows|count_summary_prepared`.
  - `count_summary_prepared` prepares the event point set and emits per-event neighbor counts/hotspots without neighbor rows.

## Why Facility KNN Is Not Included

`facility_knn_assignment` needs nearest-neighbor ranking. The current prepared fixed-radius count-threshold primitive can count or early-exit by threshold, but it cannot produce ordered KNN ranks.

Adding an OptiX surface there would be misleading unless it is explicitly classified as CUDA-through-OptiX or a new traversal-friendly KNN design is implemented. Goal810 therefore does not touch facility KNN.

## Boundary

This goal adds app surfaces and local tests. It does not create a public NVIDIA RT-core speedup claim.

The next step is to update the app matrix and later run these prepared summary paths on RTX hardware in a batched validation session.

Matrix update: the app support/readiness matrix now marks `service_coverage_gaps` and `event_hotspot_screening` as OptiX-exposed prepared-summary apps with `rt_core_partial_ready` maturity and `needs_phase_contract` benchmark readiness. They are not promoted to `rt_core_ready`.

## Verification

Completed:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal810_spatial_apps_optix_summary_surface_test tests.goal214_v0_4_application_examples_test tests.goal724_service_coverage_embree_summary_test tests.goal723_event_hotspot_embree_summary_test -v
python3 -m py_compile examples/rtdl_service_coverage_gaps.py examples/rtdl_event_hotspot_screening.py tests/goal810_spatial_apps_optix_summary_surface_test.py
git diff --check
```

Result: 15 tests OK, `py_compile` OK, and `git diff --check` OK.

Portable CPU CLI smoke checks also passed:

```bash
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference --copies 2
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend cpu_python_reference --copies 2
```
