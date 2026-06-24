# Goal 567 External Review: HIPRT Prepared Graph CSR Performance

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external AI review)
Verdict: **ACCEPT**

---

## Scope Reviewed

- `src/native/rtdl_hiprt.cpp` — `PreparedGraphCSR` struct, `prepare_graph_csr`, `run_prepared_bfs_expand`, `run_prepared_triangle_probe`, GPU kernels `RtdlBfsExpandKernel` and `RtdlTriangleProbeKernel`
- `src/rtdsl/hiprt_runtime.py` — `PreparedHiprtGraphCSR`, `prepare_hiprt_graph_csr`, `PreparedHiprtGraphKernel`
- `src/rtdsl/__init__.py` — export surface
- `tests/goal567_hiprt_prepared_graph_test.py`
- `scripts/goal567_hiprt_prepared_graph_perf.py`
- `docs/reports/goal567_hiprt_prepared_graph_perf_2026-04-18.md`
- `docs/reports/goal567_hiprt_prepared_graph_perf_linux_2026-04-18.json`
- `docs/release_reports/v0_9/support_matrix.md`
- `docs/capability_boundaries.md`
- `docs/rtdl_feature_guide.md`

---

## Correctness

### BFS Dedupe Path

The `RtdlBfsExpandKernel` GPU kernel implements the `dedupe=True` path by
gating execution to block 0 / thread 0 only (cpp:1598–1600):

```cpp
if (dedupe != 0u) {
    if (blockIdx.x != 0u || threadIdx.x != 0u) {
        return;
    }
```

Only thread 0 iterates over the full frontier in order, using `atomicCAS` to
mark discovered vertices. The `atomicCAS` is redundant (no races at single
thread) but harmless. The frontier traversal is sequential and order-preserving,
which is what gives CPU parity. This is a correct implementation of the stated
design decision: deterministic global dedupe at the cost of no GPU parallelism
on the deduplication path.

The grid is still launched at full size (`(frontier_count + 127) / 128` blocks);
non-zero threads return immediately. This wastes GPU occupancy slots but does not
affect correctness.

The `dedupe=False` parallel path (cpp:1637–1665) assigns one thread per frontier
vertex with no deduplication. This path is not used for the release-facing
comparison, consistent with the report.

### Triangle-Match Path

`RtdlTriangleProbeKernel` dispatches one GPU thread per seed
(`seed_index = blockIdx.x * blockDim.x + threadIdx.x`, cpp:1725). Each thread
fires a BVH ray from `u`, finds neighbor edges, and checks the closing edge
`(v, w)` via linear scan of `row_offsets`/`column_indices` on device. This is a
genuinely parallel kernel and correctly identifies triangles.

The `unique` flag is enforced on the CPU side after results are copied back and
sorted (cpp:4614–4621) using `std::any_of` — an O(n²) dedup pass. For the
512-vertex / 4096-edge fixture with 256 seeds this is fine. The implementation
does not claim scalability beyond this.

### Python Layer

`PreparedHiprtGraphCSR` wraps the native handle with a context manager
(`__enter__`/`__exit__`/`close`) that calls `rtdl_hiprt_destroy_prepared_graph_csr`
on exit. Resource management is correct. The empty-graph fast-path
(`column_indices == []` → returns empty `PreparedHiprtGraphCSR(empty=True)`)
avoids a null dereference on the native side.

`prepare_hiprt_graph_csr` validates `vertex_count` range and non-negativity
before calling native code. Error propagation from native status codes is handled.

`prepare_hiprt` at the high-level kernel API correctly identifies `bfs_discover`
vs other predicate names and routes to `PreparedHiprtGraphKernel`, which holds
a `PreparedHiprtGraphCSR` and forwards `frontier`/`visited` or `seeds` per call.

### Test Suite

Four tests, all `@unittest.skipUnless(hiprt_available(), ...)`:

1. `test_direct_prepared_graph_matches_bfs_cpu_reference_for_multiple_batches` —
   two frontier batches through the same prepared handle; equality vs
   `rt.bfs_expand_cpu`. This exercises the multi-call reuse pattern directly.

2. `test_direct_prepared_graph_matches_triangle_cpu_reference_for_multiple_batches` —
   two seed batches through the same prepared handle; equality vs
   `rt.triangle_probe_cpu`.

3. `test_high_level_prepare_hiprt_matches_bfs_cpu_reference` — exercises the
   full `rt.prepare_hiprt(bfs_kernel, graph=...)` surface, confirms parity vs
   `rt.run_cpu_python_reference`.

4. `test_high_level_prepare_hiprt_matches_triangle_cpu_reference` — same for
   triangle-match kernel.

The five-vertex graph fixture (vertices 0–4, 7 edges) is simple enough to verify
manually and exercises the critical BFS-level/visited interaction. Coverage of
the multi-batch reuse path in tests 1–2 is appropriate for this feature.

macOS: all 4 skip (expected). Linux evidence: 12 tests OK in 6.655s (includes
Goal 557 and 558 regression tests passing).

---

## Deterministic BFS Dedupe Boundary

The report's claim is exactly what the code implements: global dedupe with
`dedupe=True` is order-sensitive and intentionally serialized to thread 0 for
CPU parity. The boundary is correctly stated and consistently documented in:

- perf report `## Interpretation` section
- `honesty_boundary` field in the JSON
- support_matrix.md:131 ("BFS remains serialized for deterministic global dedupe")

One clarification that would improve future documentation: the serialization
happens inside the GPU kernel, not as a CPU fallback. Developers reading the
code may find this surprising — a full GPU launch where only one thread does
work. This is architecturally valid for the correctness goal of this round, but
a future BFS optimization should either implement two-pass deterministic parallel
dedupe on-GPU or move the dedupe to a CPU post-filter with parallel discovery.
This is future work, not a defect in Goal 567.

---

## Performance Claim Honesty

Numbers in the MD report were cross-checked against the JSON:

| Claim | MD Report | JSON | Match |
|---|---:|---:|---|
| BFS one-shot HIPRT | 0.669876 s | 0.669875954 s | ✓ |
| BFS prepared query median | 0.020456 s | 0.020455982 s | ✓ |
| BFS prepare phase | 0.723796 s | 0.723795981 s | ✓ |
| BFS speedup | 32.75× | 32.747191 | ✓ |
| Triangle one-shot HIPRT | 0.574389 s | 0.574389118 s | ✓ |
| Triangle prepared query median | 0.002198 s | 0.002198490 s | ✓ |
| Triangle speedup | 261.27× | 261.265286 | ✓ |

The speedups are real but correctly attributed: they represent amortization of
HIPRT setup/build/JIT cost across repeated queries, not GPU parallelism gains.
The report explicitly says so.

The report correctly discloses that BFS prepared query (0.020456 s) is still
slower than CPU (0.000722 s), Vulkan (0.002587 s), and OptiX (0.005469 s) on
this small fixture. Triangle prepared query (0.002198 s) is competitive with
OptiX (0.001827 s) and Vulkan (0.001756 s). These relative standings are
accurately reported.

The `prepare_seconds` value (0.723796 s) is shared between both BFS and triangle
results in the JSON — this is correct because one `PreparedGraphCSR` object is
built for both workloads in the perf script. The support_matrix and MD report
do not double-count prepare cost. No inflation or omission detected.

No AMD GPU claim, no RT-core speedup claim, no full-system benchmark claim.
Honesty boundary is appropriate and present both in prose and in the JSON
`honesty_boundary` field.

---

## v0.9 Doc Consistency

All three public-facing documents are consistent with the implementation:

- `docs/release_reports/v0_9/support_matrix.md`: Lines 127–134 cite correct
  numbers verbatim and correctly state "BFS remains serialized for deterministic
  global dedupe; triangle-match now uses one GPU thread per seed."

- `docs/capability_boundaries.md`: Lines 109–111 correctly include "prepared
  graph CSR paths" in the `prepare_hiprt` scope description. No overclaim.

- `docs/rtdl_feature_guide.md`: Lines 179–181 correctly list "prepared graph CSR
  paths" as part of `prepare_hiprt` coverage.

- `src/rtdsl/__init__.py`: `prepare_hiprt_graph_csr` is exported in both the
  import block and `__all__`. No documentation-vs-export gap.

---

## Issues Found

**None blocking acceptance.**

Minor observations for future consideration (not regressions, not defects):

1. `unique` triangle dedup is O(n²) on CPU post-sort. Acceptable for current
   fixture sizes; should be noted if prepared graph CSR targets larger workloads.

2. The `dedupe=True` BVH kernel launches a full grid but only thread 0 executes.
   This is waste but not a correctness issue. Future BFS work should consider a
   conditional single-block launch or CPU-side fallback.

3. `output_capacity = frontier_count * edge_count` in `run_prepared_bfs_expand`
   is a large overestimate for dense graphs with large frontiers. A tighter bound
   or device-side overflow guard would reduce memory pressure at scale.

---

## Verdict

**ACCEPT**

Goal 567 delivers a correct prepared HIPRT graph CSR context covering BFS and
triangle-match workloads. The deterministic-dedupe boundary is implemented as
described and produces verified CPU parity. Performance claims are
mathematically accurate, amortization-based, and honestly bounded. Linux
correctness evidence is present (12 tests OK). v0.9 public documentation is
consistent with the implementation and the reported numbers.
