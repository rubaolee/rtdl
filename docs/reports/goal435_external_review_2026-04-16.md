# External Review: Goal 435 v0.7 OptiX Native Prepared DB Dataset

Date: 2026-04-16
Reviewer: Claude Sonnet 4.6 (external AI, second reviewer)

## Verdict

**ACCEPT**

No blocking issues. Goal 435 satisfies its stated scope. 2-AI consensus is now met.

## Evidence Reviewed

- `src/native/optix/rtdl_optix_prelude.h` — header declarations
- `src/native/optix/rtdl_optix_api.cpp` — C ABI entry points
- `src/native/optix/rtdl_optix_workloads.cpp` — native implementation (lines 42–615)
- `src/rtdsl/optix_runtime.py` — Python binding and public API
- `tests/goal435_v0_7_optix_native_prepared_db_dataset_test.py` — correctness tests
- `docs/reports/goal435_optix_native_prepared_db_dataset_linux_2026-04-16.json` — Linux perf evidence

## Findings

**Native dataset handle.** `OptixDbDatasetImpl` owns copied field names, copied row values, primary axes, row metadata, per-row AABBs, and a built OptiX custom-primitive GAS/traversable (`accel`). The handle is created once in `create_db_dataset_optix` and released in `rtdl_optix_db_dataset_destroy`. Ownership is correct — `std::unique_ptr` guards the allocation until `release()` on success; Python destructor calls `close()` via `__del__` as a backstop.

**GAS reuse.** `db_collect_candidate_row_indices_optix_prepared` passes `dataset.accel.handle` directly to `optixLaunch` on every query call without rebuilding the BVH. This is the core claim of Goal 435, and the implementation satisfies it.

**Scan kernel JIT.** The DB scan kernel is compiled via NVRTC once per process using `std::call_once`. The first `conjunctive_scan` JSON sample (`0.4399s`) reflects this JIT cost — subsequent samples converge to ~11.5ms. This is expected behavior and does not affect the "prepare once, query many" model. The report performance table absorbs the first-sample JIT outlier into the samples list; median is computed correctly.

**Correctness.** Linux test run shows 4 tests, 0 failures, 0 skips. The four test cases cover: direct vs. prepared cross-check for all three workload shapes, repeated execution stability, and the public `prepare_optix_db_dataset` multi-query-shape API. The test correctness check in `test_public_prepared_dataset_runs_multiple_query_shapes` (line 93) uses the same predicates as `make_conjunctive_scan_case` — confirmed by reading `db_perf.py:103-111`.

**Row hash match.** JSON confirms `row_hash == postgresql_row_hash` on all three workloads, establishing correctness against PostgreSQL as an independent reference.

**Performance.** OptiX median query latency beats PostgreSQL across all three workloads (conjunctive_scan 11.6ms vs 26.3ms; grouped_count 4.5ms vs 20.2ms; grouped_sum 10.2ms vs 35.0ms). Setup-once plus 10-query totals also favor OptiX in all cases. Claims are bounded correctly: initial ingestion still uses the compatibility ctypes row-encoding path; the report and transfer_note field in the JSON both state this clearly.

**Scope boundary.** The 250000-candidate ceiling and 65536-group ceiling are enforced at runtime. The 200000-row gate fits within the 1000000-row Python-side limit.

## Non-Blocking Observations

- The first-query JIT latency for conjunctive_scan (~440ms) is larger than the GAS prepare time (~2.69s is total including table copy, axis encoding, AABB build, and GAS build). For workloads where the scan kernel has not yet been JIT-compiled, the first query cost should be communicated to users. This is a documentation gap, not a correctness or performance-gate blocker.

## Conclusion

All Goal 435 requirements are met: native OptiX prepared dataset handle, GAS reuse across repeated queries, row-exact correctness against Python truth and PostgreSQL, and Linux timing evidence. ACCEPT.
