# Goal 954: Database Native Continuation Contract

Date: 2026-04-25

## Scope

Goal954 adds explicit native-continuation metadata to the unified database app
and its two compatibility section apps.

This goal is deliberately conservative:

- Materialization-free compact DB summary paths may report native continuation.
- Full output, row output, and compact paths that still materialize grouped
  rows must report no native continuation.
- The public RT-core claim remains bounded to compact DB traversal/filter/group
  summaries only.

## Code Changes

- `examples/rtdl_v0_7_db_app_demo.py`
  - Adds `native_continuation_active`.
  - Adds `native_continuation_backend`.
  - Marks native continuation only when `output_mode=compact_summary`, backend
    is `embree`/`optix`/`vulkan`, and `run_phases` contains no materialization
    phase.

- `examples/rtdl_sales_risk_screening.py`
  - Adds the same metadata and materialization-free guard.

- `examples/rtdl_database_analytics_app.py`
  - Propagates section-level native-continuation metadata to the unified app.
  - Reports `none` unless all selected sections report materialization-free
    native continuation.

- `tests/goal954_database_native_continuation_contract_test.py`
  - Verifies regional compact summary metadata.
  - Verifies sales-risk compact summary metadata.
  - Verifies unified app propagation.
  - Verifies full CPU/Python output does not overstate native continuation.
  - Verifies a compact path that still materializes grouped rows is not marked
    native continuation.
  - Verifies a unified OptiX compact path that still materializes grouped rows
    is not marked `rt_core_accelerated`.

## Documentation Updates

- `docs/application_catalog.md`
- `docs/app_engine_support_matrix.md`
- `examples/README.md`
- `src/rtdsl/app_support_matrix.py`

The docs now say DB native-continuation metadata is active only for
materialization-free compact DB summaries.

## Verification

Focused test gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal804_db_compact_summary_scan_count_test \
  tests.goal850_optix_db_grouped_summary_fastpath_test \
  tests.goal756_prepared_db_app_session_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal690_optix_performance_classification_test -v
```

Result:

```text
Ran 24 tests in 0.356s
OK
```

Additional checks:

- `py_compile` passed for touched Python files.
- `git diff --check` passed for touched DB files.

## Boundaries

Goal954 does not claim:

- SQL engine behavior.
- DBMS behavior.
- Query optimizer, transaction, or index behavior.
- Full dashboard speedup.
- Row-materializing DB speedup.
- New public RTX speedup evidence.

## Peer-Review Blocker Fixed

The first peer review found that the unified app could report
`native_continuation_active: False` while still reporting
`rt_core_accelerated: True` for an OptiX compact run with materializing
fallback sections. The implementation now derives `rt_core_accelerated` from
the same materialization-free native-continuation backend, and the regression
is covered by
`test_unified_materializing_compact_path_is_not_rt_core_accelerated`.
