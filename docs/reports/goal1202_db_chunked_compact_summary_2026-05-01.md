# Goal1202 DB Chunked Compact Summary

Date: 2026-05-01

## Purpose

Goal1200 showed that `database_analytics` could not produce larger-scale RTX/Embree evidence because the first-wave DB lowering hit native per-job ceilings:

- 100k copies failed with `first-wave ... DB lowering exceeded the 250000-candidate ceiling`.
- 300k copies failed with the 1,000,000-row per RT job ceiling.

Goal1202 adds a bounded app/session-layer repair for the `sales_risk` compact-summary path: large prepared DB sessions are split into multiple smaller RT jobs, each still using the selected backend's prepared compact-summary traversal.

## Implementation

- `examples/rtdl_sales_risk_screening.py`
  - Adds `DB_COMPACT_SUMMARY_CHUNK_COPIES = 50000`.
  - Splits large Embree/OptiX/Vulkan `compact_summary` prepared sessions into bounded child sessions.
  - Aggregates scan count, grouped count, grouped sum, run timing, and native phase counters across chunks.
  - Emits explicit metadata:
    - `session.chunked_compact_summary`
    - `session.chunk_count`
    - `session.chunk_copies`
    - `prepared_dataset.transfer = chunked_columnar`

## Local Validation

Focused tests:

`PYTHONPATH=src:. python3 -m unittest tests/goal1202_db_chunked_compact_summary_test.py tests/goal1156_db_compact_summary_batch_contract_test.py tests/goal756_db_prepared_session_perf_test.py`

Result:

`Ran 13 tests ... OK`

Local Embree replay of the previously failing 100k sales-risk shape:

`PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 100000 --iterations 1 --output-mode compact_summary --strict --output-json /tmp/goal1202_db_embree_100000_chunked.json`

Result:

- Status: `ok`
- Chunking: `[50000, 50000]`
- Prepared row count: `600000`
- Risky scan count: `400000`
- Warm query: `0.2100161249982193` seconds on local macOS Embree

## Boundary

This is a local code repair and Embree validation only. It does not authorize public RTX speedup wording. OptiX must be rerun on a cloud RTX pod in a later consolidated batch to confirm that the DB 100k/300k probes now pass under the NVIDIA backend.
