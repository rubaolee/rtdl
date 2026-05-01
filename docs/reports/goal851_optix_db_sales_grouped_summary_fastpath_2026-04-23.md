# Goal851: OptiX DB Sales Grouped Summary Fast Path

Date: 2026-04-23

Status: implemented locally

## Problem

After Goal850, the regional dashboard compact-summary path no longer paid
grouped row materialization/sorting overhead. The `sales_risk` compact-summary
path still had the same avoidable work:

- grouped count rows were materialized;
- grouped sum rows were materialized;
- Python immediately collapsed both into summary maps.

That kept the prepared compact-summary DB path inconsistent across the two DB
scenarios.

## Change

Updated the prepared `sales_risk` session to prefer the existing OptiX grouped
summary helpers when `output_mode == "compact_summary"`:

- `grouped_count_summary(...)`
- `grouped_sum_summary(...)`

The app now:

- skips grouped row materialization for compact summary mode;
- builds the summary directly from native grouped summary outputs;
- records:
  - `query_grouped_count_summary_sec`
  - `query_grouped_sum_summary_sec`

instead of the older grouped row materialization timers when the fast path is
used.

## Files

- `/Users/rl2025/rtdl_python_only/examples/rtdl_sales_risk_screening.py`
- `/Users/rl2025/rtdl_python_only/tests/goal851_optix_db_sales_grouped_summary_fastpath_test.py`

## Verification

Ran:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal851_optix_db_sales_grouped_summary_fastpath_test \
  tests.goal850_optix_db_grouped_summary_fastpath_test \
  tests.goal804_db_compact_summary_scan_count_test \
  tests.goal756_prepared_db_app_session_test \
  tests.goal815_db_rt_core_claim_gate_test
python3 -m py_compile \
  examples/rtdl_sales_risk_screening.py \
  tests/goal851_optix_db_sales_grouped_summary_fastpath_test.py
git diff --check
```

Result: all checks passed locally.

## Why This Matters

This aligns both DB scenarios with the same compact-summary principle:

- Python should not materialize grouped rows it does not need;
- the RTDL/native path should do as much summary shaping as possible before the
  app-level summary object is formed.

This is still a local structural optimization, not a new RTX claim. The next
step is to refresh the DB profiler and internal review package so future RTX
artifacts show the new grouped-summary timers clearly.

## Boundary

This goal changes only the prepared `sales_risk` compact-summary path. It does
not authorize a public speedup claim and does not by itself promote
`database_analytics` to `rt_core_ready`.
