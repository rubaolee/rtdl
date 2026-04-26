# Goal951 Barnes-Hut Native Candidate Summary Continuation

Date: 2026-04-25

## Scope

Goal951 moves the compact Barnes-Hut candidate summary from Python set/length
summary code into the native C++ oracle ABI.

This is intentionally bounded:

- It does not implement a native Barnes-Hut opening-rule evaluator.
- It does not implement native force-vector reduction.
- It does not implement an N-body solver.
- It does not create a new RT-core claim or public speedup claim.

## Implementation

Added native ABI row/function:

- `RtdlFixedRadiusSummaryRow`
- `rtdl_oracle_summarize_fixed_radius_rows`

The Python runtime now exposes:

- `rt.summarize_fixed_radius_rows(rows)`

`examples/rtdl_barnes_hut_force_app.py` now uses this helper to summarize
fixed-radius body-to-node candidate rows into:

- `candidate_row_count`
- `body_count_with_candidates`
- `node_count_seen`

The app payload records native continuation for compact modes:

- `native_continuation_active`
- `native_continuation_backend: "oracle_cpp"`

## User-Facing Contract

RTDL still emits body-to-quadtree-node candidate rows. Native C++ continuation
now summarizes those candidate rows. Python still owns:

- Barnes-Hut opening-rule evaluation
- force-vector computation
- exact brute-force validation
- app JSON assembly

The OptiX `node_coverage_prepared` path remains the only Barnes-Hut RT-core
claim path, and it is still limited to the node-coverage decision.

## Documentation Updated

Updated:

- `docs/application_catalog.md`
- `docs/app_engine_support_matrix.md`
- `examples/README.md`
- `src/rtdsl/app_support_matrix.py`

The wording explicitly separates native C++ candidate-summary continuation from
opening-rule evaluation, force-vector reduction, N-body simulation, and speedup
claims.

## Verification

Focused Barnes-Hut/app/matrix gate:

```bash
RTDL_FORCE_ORACLE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal734_barnes_hut_embree_compact_output_test \
  tests.goal504_barnes_hut_force_app_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal817_cuda_through_optix_claim_gate_test \
  tests.goal882_barnes_hut_node_coverage_optix_subpath_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal803_rt_core_app_maturity_contract_test -v
```

Result:

```text
Ran 36 tests in 3.832s
OK
```

Additional focused matrix/source gate:

```text
Ran 9 tests in 0.001s
OK
```

Python syntax gate passed for:

- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/app_support_matrix.py`
- `examples/rtdl_barnes_hut_force_app.py`
- `tests/goal734_barnes_hut_embree_compact_output_test.py`

Whitespace gate passed for the touched Goal951 files.

## Honesty Boundary

Allowed wording:

- Barnes-Hut compact candidate summaries use native C++ continuation after RTDL
  fixed-radius candidate rows are produced.
- OptiX `node_coverage_prepared` is the bounded Barnes-Hut RT-core
  node-coverage decision path.

Disallowed wording:

- native Barnes-Hut opening-rule acceleration.
- force-vector reduction acceleration.
- N-body solver acceleration.
- new RTX/public speedup claim from this goal.
