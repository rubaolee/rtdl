# Goal880 ANN Candidate Threshold RT-Core Sub-Path

Date: 2026-04-24

## Result

Goal880 adds an explicit OptiX traversal-backed decision mode to the ANN
candidate-search app:

```bash
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py \
  --backend optix \
  --optix-summary-mode candidate_threshold_prepared \
  --candidate-radius 0.2 \
  --require-rt-core
```

This mode answers the bounded candidate-coverage query:

```text
For every query, is there at least one Python-selected candidate within radius?
```

It uses `prepare_optix_fixed_radius_count_threshold_2d(...)` over the candidate
set and runs the query points with `threshold=1`. The app still computes an
oracle coverage decision in Python for correctness validation.

## Boundary

This is not a full ANN index, not HNSW/IVF/PQ/FAISS-style search, and not a
nearest-neighbor ranking speedup. The existing ANN candidate reranking mode
still emits KNN rows and remains CUDA-through-OptiX for the OptiX backend.
Goal880 only promotes the candidate-coverage decision sub-problem to a prepared
OptiX traversal path.

No public speedup claim is authorized until a phase profiler, same-semantics
baselines, a real RTX artifact, and independent review exist.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal880_ann_candidate_threshold_rt_core_subpath_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test
```

Result: `26 tests OK`.

RTX readiness-gate tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `18 tests OK`.

Other checks:

- `py_compile`: OK for the app and new test.
- public command audit: `valid=True`.
