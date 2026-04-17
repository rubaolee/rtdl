# External Review: Goal 437 v0.7 RT DB Repeated-Query Performance Gate

Date: 2026-04-16
Reviewer: External AI (claude-sonnet-4-6)

## Verdict

ACCEPT

## Evidence Reviewed

- `docs/goal_437_v0_7_rt_db_repeated_query_perf_gate.md` — goal spec
- `docs/reports/goal437_v0_7_rt_db_repeated_query_perf_gate_2026-04-16.md` — implementation report
- `docs/reports/goal437_repeated_query_db_perf_summary_2026-04-16.json` — raw summary JSON
- `docs/reports/goal437_v0_7_rt_db_repeated_query_perf_gate_review_2026-04-16.md` — Codex review

## Findings

All stated goal requirements are satisfied:

- **PostgreSQL-inclusive Linux gate**: present. Setup time, median query time, and 10-query total are measured for PostgreSQL on `lestat-lx1` separately from RTDL prepare and query times.
- **All three backends covered**: Embree, OptiX, and Vulkan each have complete rows in every workload table.
- **Break-even discussion**: present and correctly bounded. Every backend/workload pair reports `wins_from_first_query` because RTDL prepare time is lower than PostgreSQL setup time and RTDL median query is lower than PostgreSQL median query.
- **Correctness boundary**: row-count and row-hash match PostgreSQL for all nine backend/workload pairs. Hashes are consistent across source JSON files.
- **Claim scope**: correctly limited to the in-memory, fresh-setup, bounded-kernel context. ctypes ingestion caveat is stated and the large-table transfer limitation is not suppressed.

## Notes (non-blocking)

- Embree `grouped_sum` median query speedup is 1.09x — the thinnest margin in the set. Still wins at the total-time level (3.51x). Worth watching if query count grows.
- All data is from a single machine (`lestat-lx1`). No cross-machine variance data, but that is outside the goal scope.
- Ten repeated queries is a small sample for median stability, but is the defined gate size and sufficient for the stated claim.

## Blockers

None.
