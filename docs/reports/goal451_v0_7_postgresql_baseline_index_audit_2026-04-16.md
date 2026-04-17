# Goal 451: v0.7 PostgreSQL Baseline Index Audit

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The Goal 450 PostgreSQL baseline was **indexed, not naive**, because it created
B-tree indexes on `row_id` and each predicate field and ran `ANALYZE`.

It was **not a fully tuned PostgreSQL baseline**, because it did not test
workload-specific composite or covering indexes. Goal 451 adds that audit.

## Evidence

Script:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal451_postgresql_baseline_index_audit.py`

Linux JSON evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json`

Command run on `lestat-lx1`:

```text
PYTHONPATH=src:. python3 scripts/goal451_postgresql_baseline_index_audit.py --row-count 200000 --repeats 10 --dsn dbname=postgres
```

PostgreSQL host:

- PostgreSQL 16.13.
- DSN: `dbname=postgres`.
- Row count: 200,000.
- Repeats: 10.

## Index Modes Tested

- `no_index`: temp table plus `ANALYZE`, no indexes.
- `single_column`: current Goal 450-style baseline, with `row_id` and
  per-predicate B-tree indexes.
- `composite`: workload-specific composite indexes plus a supporting `row_id`
  or `region` index where applicable.
- `covering`: workload-specific B-tree index with `INCLUDE` columns.

Each mode captured:

- setup time
- query samples
- median query time
- total setup-plus-10-query time
- row hash
- `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`

## Results

| Workload | Mode | Setup s | Median query s | Total s | Plan node path | Index statements | Hash consistent |
|---|---:|---:|---:|---:|---|---:|---|
| conjunctive_scan | no_index | 9.147 | 0.02921 | 9.440 | Sort -> Seq Scan | 0 | yes |
| conjunctive_scan | single_column | 9.062 | 0.02580 | 9.320 | Sort -> Bitmap Heap Scan -> Bitmap Index Scan | 4 | yes |
| conjunctive_scan | composite | 8.720 | 0.01642 | 8.886 | Sort -> Bitmap Heap Scan -> Bitmap Index Scan | 2 | yes |
| conjunctive_scan | covering | 9.887 | 0.02003 | 10.088 | Sort -> Bitmap Heap Scan -> Bitmap Index Scan | 1 | yes |
| grouped_count | no_index | 8.614 | 0.02238 | 8.839 | Sort -> Aggregate -> Seq Scan | 0 | yes |
| grouped_count | single_column | 8.899 | 0.01895 | 9.089 | Sort -> Aggregate -> Bitmap Heap Scan -> Bitmap Index Scan | 3 | yes |
| grouped_count | composite | 8.815 | 0.01304 | 8.945 | Sort -> Aggregate -> Bitmap Heap Scan -> Bitmap Index Scan | 2 | yes |
| grouped_count | covering | 8.677 | 0.02234 | 8.901 | Sort -> Aggregate -> Seq Scan | 1 | yes |
| grouped_sum | no_index | 9.375 | 0.03269 | 9.702 | Sort -> Aggregate -> Seq Scan | 0 | yes |
| grouped_sum | single_column | 10.594 | 0.03239 | 10.919 | Sort -> Aggregate -> Seq Scan | 3 | yes |
| grouped_sum | composite | 9.871 | 0.03258 | 10.198 | Sort -> Aggregate -> Seq Scan | 2 | yes |
| grouped_sum | covering | 8.681 | 0.03256 | 9.008 | Sort -> Aggregate -> Seq Scan | 1 | yes |

## Findings

- Goal 450 should not be described as naive SQL. It used indexed temp tables and
  `ANALYZE`.
- Goal 450 should not be described as fully tuned PostgreSQL. It used
  single-column predicate indexes, not a workload-specific index search.
- For `conjunctive_scan`, the composite index was best for both median query
  time and total setup-plus-10-query time.
- For `grouped_count`, the composite index was best for median query time, but
  no-index was slightly best for total setup-plus-10-query time because setup
  dominates at this scale.
- For `grouped_sum`, PostgreSQL chose sequential scans for every mode; the
  predicate is broad enough that indexes did not improve query time.
- All index modes produced consistent row hashes for each workload.

## Impact On Goal 450 Performance Claims

Goal 450 remains valid as a PostgreSQL-inclusive Linux comparison, but the
honest baseline wording should be:

> PostgreSQL used temp tables with per-predicate B-tree indexes and `ANALYZE`;
> this was an indexed baseline, not naive SQL, but not a maximally tuned
> PostgreSQL baseline.

For stronger future claims, compare RTDL against the best observed PostgreSQL
mode per workload:

- `conjunctive_scan`: composite index.
- `grouped_count`: composite for query-time comparison, no-index for
  setup-plus-10-query total comparison.
- `grouped_sum`: covering/no-index total comparison, with a note that the
  PostgreSQL planner used sequential scans.

## Boundary

This audit only evaluates the bounded v0.7 synthetic DB workload family. It does
not claim arbitrary SQL coverage, does not claim RTDL is a DBMS, and does not
authorize staging, tagging, merging, or release.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal451-v0_7-postgresql-baseline-index-audit.md`
