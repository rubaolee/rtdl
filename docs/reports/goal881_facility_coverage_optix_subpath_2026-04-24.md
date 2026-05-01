# Goal881 Facility Coverage OptiX Sub-Path

Date: 2026-04-24

## Result

Goal881 adds an explicit OptiX traversal-backed decision mode to the facility
KNN assignment app:

```bash
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py \
  --backend optix \
  --optix-summary-mode coverage_threshold_prepared \
  --service-radius 1.0 \
  --require-rt-core
```

This mode answers the bounded service-coverage query:

```text
For every customer, is there at least one depot within the service radius?
```

It uses `prepare_optix_fixed_radius_count_threshold_2d(...)` over depot points
and runs customer points with `threshold=1`. The app computes an oracle coverage
decision in Python for correctness validation.

## Boundary

This is not ranked nearest-depot assignment, not K=3 fallback assignment, and
not a facility-location optimizer. The existing rows, primary-assignment, and
summary modes continue to use KNN rows on CPU/Embree/SciPy surfaces. Goal881
only promotes the service-radius coverage decision sub-problem to a prepared
OptiX traversal path.

No public speedup claim is authorized until a phase profiler, same-semantics
baselines, a real RTX artifact, and independent review exist.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal881_facility_coverage_optix_subpath_test \
  tests.goal813_facility_knn_rt_core_boundary_test \
  tests.goal214_v0_4_application_examples_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal687_app_engine_support_matrix_test
```

Result: `41 tests OK`.

RTX readiness-gate tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal849_spatial_promotion_packet_test \
  tests.goal862_spatial_rtx_collection_packet_test
```

Result: `24 tests OK`.

Other checks:

- `py_compile`: OK for the app and new test.
- public command audit: `valid=True`.
