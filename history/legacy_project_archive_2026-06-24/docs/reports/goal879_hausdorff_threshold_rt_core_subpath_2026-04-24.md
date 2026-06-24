# Goal879 Hausdorff Threshold RT-Core Sub-Path

Date: 2026-04-24

## Result

Goal879 adds an explicit OptiX traversal-backed decision mode to the Hausdorff
app:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hausdorff_distance_app.py \
  --backend optix \
  --optix-summary-mode directed_threshold_prepared \
  --hausdorff-threshold 0.4 \
  --require-rt-core
```

This mode answers the decision query:

```text
Hausdorff(A, B) <= threshold ?
```

It does so by running two prepared fixed-radius threshold traversals:

- every point in `A` has at least one point in `B` within `threshold`
- every point in `B` has at least one point in `A` within `threshold`

## Boundary

This is not an exact Hausdorff-distance speedup claim. The existing exact
distance mode still emits KNN rows and remains CUDA-through-OptiX for the OptiX
backend. Goal879 only promotes the threshold decision sub-problem to an
explicit RT traversal path.

No public speedup claim is authorized until a phase profiler, same-semantics
baselines, a real RTX artifact, and independent review exist.

## Verification

Focused app and matrix tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal649_app_rewrite_anyhit_reduce_rows_test \
  tests.goal722_embree_hausdorff_summary_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test
```

Result: `38 tests OK` after adding the violating-source branch test requested
by review.

Matrix/doc focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test
```

Result: `26 tests OK`.

Other checks:

- `py_compile`: OK for the app and new test.
- `git diff --check`: OK.
- public command audit: `valid=True`.
