# External Review: Goal 440 v0.7 Embree Columnar Prepared DB Dataset Transfer

Date: 2026-04-16
Reviewer: Claude (external AI, second reviewer)

## Verdict

**ACCEPT**

No blockers. Goal 440 is complete and correctly scoped.

## Evidence Reviewed

- `src/native/embree/rtdl_embree_prelude.h` — `RtdlDbColumn` struct and `rtdl_embree_db_dataset_create_columnar` declaration present.
- `src/native/embree/rtdl_embree_api.cpp` — `rtdl_embree_db_dataset_create_columnar` implemented at line 1910; column iteration logic correct.
- `src/rtdsl/embree_runtime.py` — `transfer="columnar"` opt-in wired at line 1114; invalid mode rejected at line 1229–1230; default remains `"row"`.
- `tests/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test.py` — 4 tests: row-transfer, columnar-transfer, Python-truth parity for `conjunctive_scan`/`grouped_count`/`grouped_sum`, and invalid-mode rejection. Passed on macOS and Linux.
- `docs/reports/goal440_embree_columnar_transfer_perf_linux_2026-04-16.json` — 200k-row / 5-repeat gate on `lestat-lx1`. Columnar speedup: 3.25x (`conjunctive_scan`), 3.20x (`grouped_count`), 3.14x (`grouped_sum`). Row hashes match prior DB truth hashes.
- `docs/reports/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_2026-04-16.md` — implementation report with full claim boundary.
- `docs/reports/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_review_2026-04-16.md` — Codex ACCEPT (first AI reviewer).

## Findings

- ABI addition is additive only; existing row-struct ABI is untouched.
- Python default (`transfer="row"`) preserves backward compatibility for all existing callers.
- Correctness parity is proved by hash comparison across transfer modes for all three bounded workloads.
- Prepare-time improvement (~3.1x–3.25x on 200k rows) is material and consistent across workloads.
- Claim boundary is correctly held: Embree-only, ingestion-path improvement, not a DBMS feature. OptiX and Vulkan columnar transfer remain explicitly deferred.

## Blockers

None.
