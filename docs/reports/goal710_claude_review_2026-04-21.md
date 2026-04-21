# Goal 710: Claude Review — Embree Parallel Point-Query Implementation

Date: 2026-04-21
Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

## Files Reviewed

- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_prelude.h`
- `src/rtdsl/embree_runtime.py`
- `tests/goal710_embree_parallel_point_query_test.py`
- `scripts/goal710_embree_point_query_thread_perf.py`
- `docs/reports/goal710_embree_parallel_point_query_implementation_2026-04-21.md`
- `docs/reports/goal709_embree_threading_contract_2026-04-21.md`
- `docs/reports/goal710_embree_point_query_thread_perf_macos_2026-04-21.json`

---

## Thread Safety

**Finding: correct.**

The concern is whether multiple worker threads concurrently calling `rtcPointQuery` on a shared scene will race on callback-global state.

All four callback-globals live in `rtdl_embree_scene.cpp` lines 247–250 and are `thread_local`:

```cpp
thread_local QueryKind g_query_kind = QueryKind::kNone;
thread_local void*     g_query_state = nullptr;
thread_local bool      g_db_limit_error = false;
thread_local std::string g_db_limit_error_message;
```

Each worker thread sets its own per-thread copy of `g_query_kind` before calling `rtcPointQuery` and clears it after. Per-query state objects (`FixedRadiusNeighborsQueryState`, `KnnRowsQueryState`, etc.) are stack-allocated inside the worker lambda — each thread has its own. The `userPtr` passed to `rtcPointQuery` correctly routes to the per-thread, per-query state struct.

The Embree scene is committed before workers are launched and is read-only during the parallel loop; Embree guarantees thread-safe concurrent `rtcPointQuery` calls on a committed read-only scene.

The thread-count atomic `g_embree_thread_override` is `std::atomic<size_t>` and is loaded before any threads are spawned; it is not written during dispatch.

Worker output is partitioned into `worker_rows[worker_index]` — separate vectors, no sharing. Exception propagation uses a per-worker `exception_ptr` slot, joined cleanly after all threads complete.

No data races identified.

---

## Deterministic Row Parity

**Finding: correct.**

The output ordering is deterministic regardless of thread count:

1. **Within each query**: results are sorted by `(distance ascending, neighbor_id ascending)` using a stable comparator. This is applied per-query on each thread's local state. Floating-point distances are computed identically because the query input and search-point data are read-only.

2. **Across queries**: `run_query_ranges` concatenates worker vectors in ascending worker index order, which equals ascending query-index order (contiguous chunk assignment, no work-stealing). After concatenation the sequence is already ordered by query index.

3. **Final merge**: a `stable_sort` by `query_id` is applied. Because the concatenation order already groups all rows for the same query together and in distance/neighbor_id order, stable_sort preserves the within-query ordering while globally sorting by query_id.

Result: `threads=1` and `threads=4` produce byte-identical row sequences for any fixed input. The four new parity tests (`test_fixed_radius_2d`, `test_knn_2d`, `test_fixed_radius_3d`, `test_knn_3d`) verify this with `assertEqual`.

---

## Python configure_embree Reaches Native Code

**Finding: correctly wired end-to-end.**

The call chain:

1. `rt.configure_embree(threads=N)` stores `_EMBREE_THREAD_OVERRIDE = N` and, if the library is already loaded (`lru_cache` hit), immediately calls `_apply_embree_thread_config`.
2. `_apply_embree_thread_config(library, config)` calls `library.rtdl_embree_configure_threads(ctypes.c_size_t(config.effective_threads))`.
3. `rtdl_embree_configure_threads(size_t thread_count)` stores to `g_embree_thread_override` (atomic).
4. `embree_dispatch_thread_count(work_count)` loads from `g_embree_thread_override`; if zero, falls back to `parse_embree_env_threads()`; caps at `work_count`.

Both `PreparedEmbreeExecution.run()` and `run_raw()` call `_apply_embree_thread_config(self.library)` at their first line, so any change to the Python-level override made after preparation (e.g., `configure_embree` called between a `prepare_embree` and a `run`) is pushed to native before each invocation. The test `tearDown` clears the override with `rt.configure_embree(threads=None)`, which correctly restores auto-detection.

The `ctypes` argtypes declaration for `rtdl_embree_configure_threads` (`c_size_t → None`, `embree_runtime.py` line 2878) matches the native signature.

If the library has not yet been loaded when `configure_embree` is called, the Python override is stored and will be applied by `_load_configured_embree_library()` at first load. No timing hole.

---

## Performance Claims

**Finding: honest and well-scoped.**

Numbers cross-checked against `goal710_embree_point_query_thread_perf_macos_2026-04-21.json`:

| Workload | 1 thread | auto threads | Speedup (reported) | Speedup (JSON) |
|---|---:|---:|---:|---:|
| fixed_radius_neighbors | 0.011468 s | 0.009231 s | 1.24× | 1.2423× |
| knn_rows | 1.221234 s | 0.224760 s | 5.43× | 5.4335× |

The report's rounded figures match the JSON exactly.

The report accurately qualifies:
- Fixed-radius gains are "too short at this scale for a strong performance claim" and treated as "smoke-level local signal."
- KNN gains are substantial because each query does heavier traversal with an infinite initial radius.
- All results are macOS Embree CPU only; no RT-core claim is made.
- The benchmark ran on a 10-thread machine (`effective_threads: 10`), which explains the super-linear KNN result at `auto`.

---

## Scope / Boundary Honesty

**Finding: accurate.**

The report correctly limits Goal710 to the four point-query functions and explicitly names the remaining kernels (ray-query, segment/polygon, graph, DB) as not yet parallelized. No overclaim on coverage or RT-core involvement.

---

## Minor Observations (Non-Blocking)

1. **`point_point_query_collect` fall-through**: When `g_query_kind` is not `kFixedRadiusNeighbors`, the callback falls through to an unconditional `KnnRowsQueryState` cast. A caller that accidentally sets an unexpected `g_query_kind` (e.g., from a different kernel) would silently produce incorrect results. This is a pre-existing condition not introduced by Goal710 and is safe in practice because each dispatch function sets its own `g_query_kind` via `thread_local`.

2. **No 3D performance numbers in the benchmark script**: The perf script (`goal710_embree_point_query_thread_perf.py`) measures 2D workloads only. This is not a honesty problem — the report does not claim 3D performance results — but a future iteration could add 3D coverage.

3. **Test case sizes are small**: 12 query points and 18 query points respectively. These are correctness-only cases; the performance numbers come from the separate benchmark. No concern.

---

## Verdict

**ACCEPT.**

Thread safety is correct (`thread_local` callback state, read-only scene, per-worker output vectors). Determinism is provably preserved by the chunk-partition and stable merge strategy. The Python→native configuration path is correctly wired and re-applied before every dispatch. Performance numbers are reproducible and honestly scoped to macOS Embree CPU with appropriate caveats.
