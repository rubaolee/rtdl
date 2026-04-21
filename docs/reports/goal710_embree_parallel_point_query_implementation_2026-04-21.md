# Goal 710: Embree Parallel Point-Query Implementation

Date: 2026-04-21
Status: accepted by Codex, Claude, and Gemini Flash

## Purpose

Goal710 starts the Embree multicore execution path required by the v1.0
pre-goal. It implements native multithreaded dispatch for the first agreed
kernel family from Goal708/Goal709:

- `rtdl_embree_run_fixed_radius_neighbors`
- `rtdl_embree_run_fixed_radius_neighbors_3d`
- `rtdl_embree_run_knn_rows`
- `rtdl_embree_run_knn_rows_3d`

These cover the most app pressure among the local Embree point-query apps and
exercise the hardest common problem: variable-length row output with exact,
deterministic merge order.

## Implementation

Native changes:

- Added exported native setter `rtdl_embree_configure_threads(size_t)`.
- Added native dispatch helper that resolves thread count from:
  - Python API bridge, or
  - `RTDL_EMBREE_THREADS`, or
  - hardware concurrency.
- Partitioned query units into contiguous ranges.
- Used one worker per range.
- Used per-worker row vectors.
- Merged worker vectors in ascending range order.
- Preserved the existing stable final sort by `query_id`.
- Kept Embree scenes committed once and read-only during parallel query
  dispatch.
- Relied only on thread-safe callback state for the parallelized point-query
  path:
  - `g_query_kind`, `g_query_state`, `g_db_limit_error`, and
    `g_db_limit_error_message` are declared `thread_local` in
    `src/native/embree/rtdl_embree_scene.cpp`;
  - fixed-radius/KNN per-query state is stack-local inside each worker and is
    passed to Embree through `args->userPtr`;
  - the shared search-point vectors and committed Embree scene are read-only
    during dispatch.

Python bridge:

- `rt.configure_embree(threads=...)` now applies to a loaded native Embree
  library through `rtdl_embree_configure_threads`.
- Prepared Embree executions re-apply current config before `run()` and
  `run_raw()`, so changing the thread count after preparation is honored.
- `rt.embree_version()` and `rt.run_embree(...)` load a configured native
  library.

## Correctness Verification

Ran:

```bash
make build-embree
PYTHONPATH=src:. python3 -m unittest -v tests.goal200_fixed_radius_neighbors_embree_test tests.goal206_knn_rows_embree_test tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal300_v0_5_embree_3d_knn_test tests.goal709_embree_threading_contract_test tests.goal710_embree_parallel_point_query_test
python3 -m py_compile src/rtdsl/embree_runtime.py tests/goal710_embree_parallel_point_query_test.py scripts/goal710_embree_point_query_thread_perf.py
git diff --check
```

Result:

- Embree built and probed as `4.4.0` on this macOS machine.
- 28 focused Embree point-query/threading tests passed.
- Python compile checks passed.
- Diff whitespace check passed.

New parity tests explicitly compare `threads=1` versus `threads=4` for:

- 2D fixed-radius neighbors;
- 2D KNN rows;
- 3D fixed-radius neighbors;
- 3D KNN rows.

## Local Performance Evidence

Benchmark script:

```bash
PYTHONPATH=src:. python3 scripts/goal710_embree_point_query_thread_perf.py --queries 4000 --search 12000 --iterations 3 --output docs/reports/goal710_embree_point_query_thread_perf_macos_2026-04-21.json
```

Machine-observed median results:

| Workload | Rows | 1 thread | 2 threads | 4 threads | auto threads |
|---|---:|---:|---:|---:|---:|
| fixed_radius_neighbors | 12,000 | 0.011468s | 0.010723s | 0.010180s | 0.009231s |
| knn_rows | 12,000 | 1.221234s | 0.617975s | 0.344126s | 0.224760s |

Speedup versus one thread:

- fixed-radius: `auto` was `1.24x`.
- KNN: `auto` was `5.43x`.

Interpretation:

- KNN shows the intended multicore benefit because each query performs heavier
  candidate work.
- Fixed-radius is too short at this scale for a strong performance claim; the
  result is positive but should be treated as a smoke-level local signal.
- This is macOS Embree CPU evidence only. It is not NVIDIA RT-core evidence.

## Boundary

Goal710 is an Embree CPU RT/BVH multicore improvement. It does not change any
NVIDIA RT-core app claim. It also does not complete the full Embree app
coverage target: ray-query, segment/polygon, graph, and DB kernels still need
separate parallel dispatch work or explicit exclusion.

## Review Closure

- Claude review: `docs/reports/goal710_claude_review_2026-04-21.md`,
  verdict ACCEPT.
- Gemini initial review:
  `docs/reports/goal710_gemini_flash_review_2026-04-21.md`, verdict BLOCK
  due a shared-global thread-safety concern.
- Gemini re-review:
  `docs/reports/goal710_gemini_flash_rereview_2026-04-21.md`, verdict ACCEPT
  after verifying the callback variables are `thread_local` and fixed-radius /
  KNN state is passed via `args->userPtr`.
- Codex consensus closure:
  `docs/reports/goal710_codex_consensus_closure_2026-04-21.md`, verdict
  ACCEPT.
