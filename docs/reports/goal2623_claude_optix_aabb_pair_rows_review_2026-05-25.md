I now have a complete picture across all layers. Here is the review.

---

## Goal2623 Review: OptiX `AABB_INDEX_QUERY_2D` `range_intersection_rows`

### Finding 1 — LOW: Overflow fires on pre-dedup raw count, not deduped pair count

**Where:** `rtdl_optix_workloads.cpp:7870–7878`, `optix_runtime.py:8082–8086`

The bidirectional-pass design (forward pass: query-rays vs. indexed-GAS; backward pass: indexed-rays vs. query-GAS) is correct, but both passes increment the same atomic counter. An AABB pair that is detected by both passes counts twice in `raw_count`. The host overflow check fires when `raw_count > row_capacity`, not when `deduped_count > row_capacity`. A caller who sets `row_capacity = N_true_pairs` may see a spurious overflow because the raw count can reach `2 × N_true_pairs`.

The app works around this with `resolved_row_capacity = max(1, 2 × scene, 2 × query)`, which is tight but holds for the grid fixture. This design tradeoff is not documented anywhere — not in the report, not in the primitive catalog entry, not in the Python docstring. Callers who hand-tune capacity can hit this without a clear explanation.

**Fix:** Add one sentence to the report's "Overflow contract" section and to the `aabb_intersection_pair_rows_2d` docstring: *"Capacity must accommodate the pre-deduplication bidirectional-pass count, which can reach up to 2× the true pair count."*

---

### Finding 2 — LOW: No persistent GPU-path overflow regression test

**Where:** `tests/goal2623_optix_aabb_pair_rows_test.py`

`goal2622` has `test_aabb_broadphase_overflow_still_fails_closed` which tests the CPU overflow path. Goal2623 adds no `@skipUnless(gpu_available)` analogue that deliberately triggers OptiX overflow. The overflow was verified on-pod (report shows the correct `failure_mode=fail_closed_overflow` message), but that probe is not reproducible in CI. If someone changes the overflow signaling, no persistent test catches it.

**Fix:** Add a GPU-skipped test that calls `collect_range_intersection_rows` with `row_capacity=1` on an index with 2+ intersecting pairs and asserts `RuntimeError` with `failure_mode=fail_closed_overflow`.

---

### Finding 3 — INFO: No `static_assert` on `RtdlAabbPairRow` layout

**Where:** `rtdl_optix_prelude.h:101–104`

`RtdlFixedRadiusNeighborRow`, `RtdlKnnNeighborRow`, and others all have `static_assert` guards on offsets and total size. `RtdlAabbPairRow` (`uint32_t query_id; uint32_t indexed_id;` = 8 bytes) has none. There is also a shadow definition inside the CUDA device kernel source string (`workloads.cpp:7231`) that must stay layout-compatible with the C ABI struct but is not checked.

**Fix:** Add `static_assert(sizeof(RtdlAabbPairRow) == 8)` and offset asserts in `rtdl_optix_prelude.h`, consistent with the existing pattern.

---

### Everything-else pass (confirmed correct)

| Dimension | Result |
|---|---|
| App-agnosticism | Clean. Device kernel uses only `box_queries[...].id` / `indexed_boxes[...].id`. Static text test locks this in. |
| Fail-closed on overflow | Correct at all layers: device kernel only writes within capacity bounds; host sets `*overflowed_out=1` and returns before any `memcpy`; Python raises with `failure_mode=fail_closed_overflow`. No partial row table is ever returned. |
| `row_capacity=0` with non-null input | `DevPtr(0)` skips allocation (core.cpp:73); device kernel guard `row_index < 0` never fires; host overflow check fires correctly. Consistent if undocumented. |
| `native_engine_customization: False` | Correctly set in all return dicts. |
| `claim_boundary` field | Present and accurate in both Python layers. |
| ctypes argtypes | `POINTER(_RtdlAabbPairRow)` correctly wired (optix_runtime.py:12547). `_RtdlAabbPairRow` fields match C struct. |
| Primitive catalog entry | Accurate and includes the fail-closed overflow note. |
| Application catalog entry | Accurate; correctly says "no native contact/collision ABI." |
| Pod evidence | 16 tests pass on RTX A5000, including overflow probe. |

---

**Verdict: ACCEPT WITH ISSUES**

The implementation is correct, the fail-closed contract holds at all three layers (device, host, Python), and the app-agnostic boundary is clean and test-locked. Both open issues (pre-dedup capacity documentation, missing GPU overflow regression test) are low severity and do not compromise correctness or safety of the current code. They should be tracked but do not block promotion.
