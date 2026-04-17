# External Review: Goal 434 v0.7 Embree Native Prepared DB Dataset

Date: 2026-04-16
Reviewer: Claude Sonnet 4.6 (external AI, second reviewer)

## Verdict

**ACCEPT**

No release-blocking issues found. Goal 434 satisfies its required outcome and the 2-AI consensus requirement is met.

---

## Evidence Reviewed

- `src/native/embree/rtdl_embree_prelude.h` — C ABI declarations
- `src/native/embree/rtdl_embree_api.cpp` — native implementation
- `src/rtdsl/embree_runtime.py` — Python wrapper
- `src/rtdsl/__init__.py` — public export
- `tests/goal434_v0_7_embree_native_prepared_db_dataset_test.py` — test suite
- `docs/reports/goal434_embree_native_prepared_db_dataset_linux_2026-04-16.json` — perf gate
- `docs/reports/goal434_v0_7_embree_native_prepared_db_dataset_2026-04-16.md` — implementation report

---

## Findings

### Native ABI (prelude.h + rtdl_embree_api.cpp)

All five C ABI functions are declared in the header and implemented:
- `rtdl_embree_db_dataset_create` — allocates `EmbreeDbDatasetImpl`, copies table, encodes primary axes, builds row boxes, and calls `rtcCommitScene` exactly once via `db_attach_dataset_scene` (line 310).
- `rtdl_embree_db_dataset_destroy` — `delete`s the impl.
- `rtdl_embree_db_dataset_conjunctive_scan`, `_grouped_count`, `_grouped_sum` — each calls `rtcIntersect1` against `impl->holder.scene` directly (scene not rebuilt per query). Verified at lines 1882–1888 and analogous blocks.

Scene-reuse claim is sound: `rtcCommitScene` is not called in any query function; only the create path commits the scene.

### Python API

`PreparedEmbreeDbDataset` at `embree_runtime.py:1180` owns the native handle and exposes `conjunctive_scan`, `grouped_count`, `grouped_sum`, and `close`. `prepare_embree_db_dataset` is exported in `__init__.py` (line 105, 628).

### Tests

4 tests cover: direct-vs-reference, prepared-vs-reference, repeated-execution stability, and public multi-query-shape API — all on macOS and Linux. `test_public_prepared_dataset_runs_multiple_query_shapes` closes the dataset in a `finally` block and asserts all three query shapes against Python truth. Test design is appropriate for the goal scope.

### Linux PostgreSQL Performance Gate

JSON is internally consistent:
- `"row_count": 200000` (top-level input size) is correctly distinct from per-workload output row counts.
- Row hashes match between Embree and PostgreSQL for all three workloads (`conjunctive_scan`: `19461bd…`, `grouped_count`: `869ed4…`, `grouped_sum`: `123b2f…`), confirming correctness parity on Linux.
- Embree prepare times (~2.8–2.9 s) plus 10 × median query times are consistent with reported totals (~3.1 s); no arithmetic anomalies.
- PostgreSQL wins per-query latency for `conjunctive_scan` (29 ms vs 19 ms) and `grouped_sum` is near-parity (38 ms vs 35 ms); Embree wins the total-session metric because PostgreSQL setup is ~4× heavier. This is correctly stated in the report.

### Boundary / Caveat Check

The ingestion-path caveat (ctypes row encoding, not a columnar transfer path) is correctly documented in the JSON `transfer_note` field and in the report interpretation section. The performance claim is appropriately bounded; no overstated large-table ingestion claims are present.

---

## Blockers

None.

---

## Follow-up Notes (non-blocking)

The report correctly identifies Goals 435 and 436 (OptiX, Vulkan prepared dataset) as the parallel application of this pattern, and defers columnar ingestion to a later goal. Both are appropriate scope boundaries for Goal 434.
