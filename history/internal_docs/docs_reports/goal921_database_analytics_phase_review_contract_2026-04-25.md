# Goal921: Database Analytics Phase Review Contract

Date: 2026-04-25

## Result

Goal921 keeps `database_analytics` in `rt_core_partial_ready` / `needs_interface_tuning`, but improves the pre-cloud and post-cloud evidence contract for the prepared compact-summary DB path.

The profiler now emits:

- `schema_version: goal921_db_phase_review_contract_v2`
- `reported_run_phase_totals_sec`
- `reported_native_db_phase_totals_sec`
- `db_review_observation`

The Goal762 artifact analyzer now preserves those fields when reading future RTX cloud DB artifacts.

## Why This Was Needed

The DB app already has real OptiX DB BVH candidate discovery and native C++ exact filtering/grouping. The remaining release question is not whether there is an OptiX path; it is whether the bounded compact-summary path has clean enough phase evidence to claim RT-core-backed usefulness without hiding Python/ctypes/materialization cost.

Before Goal921, reviewers had to manually inspect nested JSON to answer:

- whether the warm-query path used row materialization or compact summaries,
- whether native OptiX DB counters were exported,
- how much query/postprocess time was recorded,
- whether the artifact should be treated as a claim candidate or held.

Goal921 makes those answers explicit and machine-readable.

## Local Observation

A portable local CPU sample was written to:

```text
docs/reports/goal921_db_phase_review_contract_local_sample_2026-04-25.json
```

This sample intentionally does not claim RT-core acceleration. It records that the CPU backend still uses row-materializing operations even in compact-summary output mode:

```text
db_review_observation.status = needs_interface_tuning
row_materializing_operation_count = 3
native_counter_status = empty
```

For OptiX RTX cloud artifacts, the desired observation is:

```text
phase_clean_candidate_for_rtx_review
```

That requires compact-summary operation modes plus exported native DB phase counters.

## Files

Updated:

```text
scripts/goal756_db_prepared_session_perf.py
scripts/goal762_rtx_cloud_artifact_report.py
tests/goal756_db_prepared_session_perf_test.py
tests/goal762_rtx_cloud_artifact_report_test.py
tests/goal825_tier1_profiler_contract_test.py
docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
```

Added:

```text
docs/reports/goal921_db_phase_review_contract_local_sample_2026-04-25.json
```

## Boundary

This is an evidence-quality and review-contract improvement, not a DB readiness promotion.

No public DB speedup claim is authorized by this goal. The DB app remains partial until a real RTX artifact shows compact-summary operation modes, exported native DB phase totals, correctness parity, and acceptable comparison against CPU/Embree/PostgreSQL same-semantics baselines.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal756_db_prepared_session_perf_test \
  tests.goal825_tier1_profiler_contract_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal804_db_compact_summary_scan_count_test \
  tests.goal850_optix_db_grouped_summary_fastpath_test \
  tests.goal851_optix_db_sales_grouped_summary_fastpath_test \
  tests.goal815_db_rt_core_claim_gate_test
```

Result: `42 tests OK`.

Compile and whitespace checks:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal756_db_prepared_session_perf.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  tests/goal756_db_prepared_session_perf_test.py \
  tests/goal762_rtx_cloud_artifact_report_test.py \
  tests/goal825_tier1_profiler_contract_test.py

git diff --check
```

Result: `OK`.
