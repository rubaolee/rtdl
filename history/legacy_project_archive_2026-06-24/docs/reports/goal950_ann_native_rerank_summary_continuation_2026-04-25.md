# Goal950 ANN Native Rerank Summary Continuation

Date: 2026-04-25

## Scope

Goal950 moves the compact ANN candidate rerank summary from Python set/max
summary code into the native C++ oracle ABI.

This is intentionally bounded:

- It does not implement an ANN index.
- It does not move Python candidate-set construction into RTDL.
- It does not move exact full-set quality comparison into RTDL.
- It does not claim KNN ranking speedup.
- It does not create a new RT-core claim.

## Implementation

Added native ABI row/function:

- `RtdlKnnSummaryRow`
- `rtdl_oracle_summarize_knn_rows`

The Python runtime now exposes:

- `rt.summarize_knn_rows(rows)`

The ANN app now uses this helper for the compact rerank summary fields:

- `approximate_row_count`
- `query_count_with_candidate`
- `max_neighbor_rank`

The app payload records:

- `native_continuation_active: True`
- `native_continuation_backend: "oracle_cpp"`

for the non-OptiX-threshold candidate-rerank path where the native summary is
used.

## User-Facing Contract

`examples/rtdl_ann_candidate_app.py` still demonstrates candidate-subset KNN
reranking over a Python-selected candidate subset. The new native continuation
only summarizes emitted KNN rows. Python still owns:

- candidate-set construction
- exact full-set KNN baseline for quality comparison
- recall and distance-ratio policy
- app JSON assembly

The OptiX `candidate_threshold_prepared` path remains the only ANN RT-core claim
path, and it is still limited to the candidate-coverage decision.

## Documentation Updated

Updated:

- `docs/application_catalog.md`
- `docs/app_engine_support_matrix.md`
- `examples/README.md`

The wording explicitly separates native C++ rerank summaries from ANN indexing,
candidate construction, quality policy, and ranking speedup claims.

## Verification

Focused ANN/app/matrix gate:

```bash
RTDL_FORCE_ORACLE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal735_ann_candidate_compact_output_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal520_dbscan_clustering_app_test \
  tests.goal880_ann_candidate_threshold_rt_core_subpath_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal803_rt_core_app_maturity_contract_test -v
```

Result:

```text
Ran 35 tests in 1.285s
OK
```

Python syntax gate passed for:

- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/__init__.py`
- `examples/rtdl_ann_candidate_app.py`
- `tests/goal735_ann_candidate_compact_output_test.py`

Whitespace gate passed for the touched Goal950 files.

## Honesty Boundary

Allowed wording:

- ANN compact rerank summaries use native C++ continuation after RTDL KNN rows
  are produced.
- OptiX `candidate_threshold_prepared` is the bounded ANN RT-core candidate
  coverage decision path.

Disallowed wording:

- ANN index acceleration.
- KNN ranking speedup.
- candidate construction acceleration.
- recall/latency optimizer.
- new RTX speedup claim from this goal.
