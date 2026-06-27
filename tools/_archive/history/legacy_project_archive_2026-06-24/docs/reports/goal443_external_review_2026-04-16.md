# External Review: Goal 443 v0.7 Columnar Repeated-Query Performance Gate

Date: 2026-04-16
Reviewer: Claude (external AI, second review for 2-AI consensus)

## Verdict

**ACCEPT**

No blockers. Goal 443 satisfies all stated requirements. This is the second of the two required AI reviews; consensus is met.

---

## Checklist Against Goal 443 Requirements

| Requirement | Status |
|---|---|
| Goal 437 preserved as historical row-transfer evidence | PASS — `docs/reports/goal437_*` files and `scripts/goal437_*` are intact and unmodified |
| New Linux artifact with Embree, OptiX, Vulkan using `transfer="columnar"` | PASS — `goal443_columnar_repeated_query_perf_linux_2026-04-16.json` present; all nine backend/workload entries include `"*_dataset_transfer": "columnar"` |
| PostgreSQL setup/query included on Linux | PASS — `postgresql_setup_seconds` and `postgresql_query_seconds_*` present in every workload |
| All three bounded workloads: `conjunctive_scan`, `grouped_count`, `grouped_sum` | PASS |
| prepare/setup once, median query, total repeated time, correctness hash equality reported | PASS — `*_dataset_prepare_seconds`, `*_dataset_query_seconds_median`, `*_dataset_total_repeated_seconds`, `row_hash` present for every backend |
| Claim boundary preserved | PASS — report explicitly excludes DBMS, arbitrary SQL, and PostgreSQL-level durability/concurrency/indexing claims |

---

## Script Review (`goal443_columnar_repeated_query_perf_gate.py`)

**Transfer enforcement.** `_measure_backend` passes `transfer="columnar"` at line 62 on every `prepare_fn` call. No path allows row transfer to slip through.

**Correctness enforcement.** Two independent hash checks are performed:

1. `_measure_workload` checks PostgreSQL row-count and row-hash against the Python reference truth before any backend is measured (line 131–132).
2. `_attach_postgresql` checks each backend's row-count and row-hash against the PostgreSQL report (line 93–94), raising `AssertionError` on mismatch.

This means all four outputs (Python, PostgreSQL, Embree, OptiX, Vulkan) must agree on both row-count and hash, or the script aborts.

**Reuse of PostgreSQL helpers.** The script imports `measure_postgresql_scan_once`, `measure_postgresql_grouped_count_once`, and `measure_postgresql_grouped_sum_once` from Goal 434. This is appropriate: those helpers are already externally reviewed and tested.

**Median calculation.** `median_seconds` is used, not mean. With 10 samples this correctly suppresses the known first-query warm-up spike observed in GPU backends (see JSON observations below).

---

## JSON Artifact Review (`goal443_columnar_repeated_query_perf_linux_2026-04-16.json`)

**Top-level fields verified:**

- `"goal": 443` ✓
- `"transfer": "columnar"` ✓
- `"row_count": 200000` ✓
- `"repeated_query_count": 10` ✓

**Hash consistency verified across all workloads:**

| Workload | Reference rows | Reference hash | PostgreSQL matches | All backends match |
|---|---|---|---|---|
| conjunctive_scan | 22,268 | `19461bdd…` | ✓ | ✓ |
| grouped_count | 8 | `869ed487…` | ✓ | ✓ |
| grouped_sum | 8 | `123b2f6f…` | ✓ | ✓ |

**Break-even:** All nine backend/workload combinations report `"wins_from_first_query"`, meaning RTDL total time (prepare + 10 queries) beats PostgreSQL total time (fresh setup + 10 queries) starting from query one.

**Total speedup vs PostgreSQL (all positive, all > 6x):**

| Workload | Embree | OptiX | Vulkan |
|---|---|---|---|
| conjunctive_scan | 10.01x | 6.84x | 7.21x |
| grouped_count | 12.56x | 14.01x | 13.81x |
| grouped_sum | 9.18x | 11.37x | 11.03x |

**Observations (non-blocking):**

1. **GPU first-query warm-up.** OptiX and Vulkan exhibit a large first-query spike in `conjunctive_scan` (OptiX sample[0] ≈ 0.418 s vs median 0.012 s; Vulkan sample[0] ≈ 0.327 s vs median 0.014 s). This is expected GPU JIT/shader-compilation behavior. The use of median over 10 samples correctly suppresses this artifact, and all samples are preserved in the JSON for reader inspection. No correction needed.

2. **Embree median query speedup is modest in isolation.** Embree's per-query median speedup over PostgreSQL is 1.15x–1.65x (CPU backend vs CPU PostgreSQL). The large total speedup (9–13x) is driven by PostgreSQL's 10–12 s fresh-setup cost dwarfing RTDL's 0.82–0.87 s prepare time. This is accurate and the report does not overstate it.

3. **OptiX `optix_dataset_total_repeated_seconds` includes the first-query spike.** For conjunctive_scan, OptiX total is 1.515 s, which includes the 0.418 s outlier in sample[0]. This is honest accounting and is correctly reported.

---

## Dependency Chain Verified

- Goal 440 (Embree columnar transfer): external review ACCEPT present (`goal440_external_review_2026-04-16.md`) ✓
- Goal 441 (OptiX columnar transfer): external review present (`docs/reports/goal441_*`) ✓
- Goal 442 (Vulkan columnar transfer): external review present (`docs/reports/goal442_*`) ✓
- Goal 437 (row-transfer gate): untouched, historical record preserved ✓

---

## Claim Boundary Confirmation

The implementation report and this JSON artifact are correctly bounded to:

- Linux host (lestat-lx1)
- 200,000-row synthetic dataset
- Three specific workload kernels (conjunctive scan, grouped count, grouped sum)
- Fresh-setup + 10-query repeated measurement paradigm
- In-memory workload comparison, not a DBMS benchmark

The excluded claims (full DBMS semantics, arbitrary SQL, durability, concurrency, query planning, indexing, transactions) are explicitly listed and not implied by any number in the artifact.

---

## Blockers

None.

## Final Decision

**ACCEPT.** Goal 443 is closed. The 2-AI consensus requirement is satisfied (Codex ACCEPT + this external AI ACCEPT).
