# External Review: Goal 436 v0.7 Vulkan Native Prepared DB Dataset

Date: 2026-04-16
Reviewer: External AI (Claude Sonnet 4.6)

## Verdict

**ACCEPT**

No blockers found.

## Evidence Reviewed

- `docs/goal_436_v0_7_vulkan_native_prepared_db_dataset.md` — goal spec
- `docs/reports/goal436_v0_7_vulkan_native_prepared_db_dataset_2026-04-16.md` — implementation report
- `docs/reports/goal436_v0_7_vulkan_native_prepared_db_dataset_review_2026-04-16.md` — codex review
- `docs/reports/goal436_vulkan_native_prepared_db_dataset_linux_2026-04-16.json` — Linux perf JSON
- `src/native/vulkan/rtdl_vulkan_prelude.h` — C ABI declarations
- `src/native/vulkan/rtdl_vulkan_api.cpp` — C ABI implementations
- `tests/goal436_v0_7_vulkan_native_prepared_db_dataset_test.py` — test suite

## Findings

**Correctness:** Row hashes match between Vulkan and PostgreSQL for all three workloads at 200,000 rows:
- `conjunctive_scan`: 22,268 rows, hash `19461b...` ✓
- `grouped_count`: 8 rows, hash `869ed4...` ✓
- `grouped_sum`: 8 rows, hash `123b2f...` ✓

**Tests:** 4 tests pass on Linux (`lestat-lx1`) in 0.704s. Coverage includes direct vs reference correctness, prepared vs reference correctness, repeated execution stability, and multi-shape query exercise on a single dataset handle.

**Native ABI:** All five required C functions are declared in the prelude and implemented in `rtdl_vulkan_api.cpp`: `create`, `destroy`, `conjunctive_scan`, `grouped_count`, `grouped_sum`.

**Performance (Linux, 200k rows, 10 repeats):**

| Workload | Vulkan median query | PG median query | Vulkan total | PG total |
|---|---:|---:|---:|---:|
| conjunctive_scan | 13.6 ms | 26.5 ms | 3.22 s | 10.41 s |
| grouped_count | 7.0 ms | 20.4 ms | 2.68 s | 10.25 s |
| grouped_sum | 13.5 ms | 35.3 ms | 2.60 s | 13.01 s |

Vulkan wins median query latency and prepare-once + 10-query total for all three workloads. The first `conjunctive_scan` sample (329 ms) is a visible warm-up outlier; the median correctly excludes it.

**Boundary:** The ctypes compatibility row ingestion caveat is correctly stated in both the report and the JSON `transfer_note` field. The claim is scoped to BLAS/TLAS reuse and repeated-query latency, not large-table ingestion throughput.

## Notes

None. Goal 433 contract is satisfied for the Vulkan backend. Goal 437 (cross-backend repeated-query gate) is the appropriate follow-up.
