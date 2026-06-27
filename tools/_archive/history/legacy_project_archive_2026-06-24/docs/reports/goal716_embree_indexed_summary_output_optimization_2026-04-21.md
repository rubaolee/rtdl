# Goal 716: Embree Indexed Summary Output Optimization

Date: 2026-04-21

## Scope

Goal716 is a follow-up to Goal715. Goal715 added a native Embree fixed-radius count/threshold summary primitive, but the implementation reused the generic variable-row parallel helper. That helper is appropriate for neighbor rows, but it is unnecessary for summary rows because the output cardinality is exactly one row per query.

Goal716 changes the native Embree summary path to write summary rows directly by query index.

## Code Change

- Added `run_query_index_ranges(...)` to `src/native/embree/rtdl_embree_api.cpp`.
- Changed `rtdl_embree_run_fixed_radius_count_threshold` from per-worker local vectors plus merge into direct indexed writes:
  - allocate `std::vector<RtdlFixedRadiusCountRow> rows(query_values.size())`
  - each worker writes `rows[query_index]`
  - no worker row-vector merge
  - no row-order repair pass needed
- Updated the Goal715 source-inspection test to check the indexed helper.

## Correctness

Focused validation:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal715_embree_fixed_radius_summary_test
Ran 3 tests
OK
```

The existing app-level oracle parity for outlier and DBSCAN summary modes remains valid.

## Local Native Timing

Command:

```text
PYTHONPATH=src:. python3 scripts/goal715_embree_fixed_radius_summary_perf.py --copies 512,2048,8192,32768 --repeats 5 --warmups 1 --output docs/reports/goal716_embree_fixed_radius_indexed_summary_perf_local_2026-04-21.json
```

Comparison against the previous local Goal715 summary run:

| copies | Goal715 outlier summary vs rows | Goal715 DBSCAN summary vs rows | Goal716 outlier summary vs rows | Goal716 DBSCAN summary vs rows |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 0.928x | 1.063x | 1.174x | 1.267x |
| 2048 | 0.902x | 1.071x | 0.806x | 1.354x |
| 8192 | 0.919x | 1.111x | 0.842x | 1.030x |
| 32768 | 0.856x | 1.043x | 0.755x | 1.294x |

## Interpretation

The indexed-output optimization improves the core-flag DBSCAN summary path in this local run. It does not turn sparse outlier detection into a reliable speedup because the row path already emits only a small number of rows per query, while summary mode emits one row for every query and still pays Embree point-query traversal.

Honest claim boundary:

- Correct: Embree now has a lower-overhead fixed-cardinality summary output path.
- Correct: DBSCAN core-flag mode shows local native timing improvement versus neighbor-row mode.
- Not correct: claiming a universal fixed-radius summary speedup.
- Not correct: claiming full DBSCAN clustering acceleration, because cluster expansion remains Python-owned.

## Status

Goal716 is implemented and locally validated. The next performance target should be prepared/reused scenes or app-level compact output modes, not more row-output plumbing.
