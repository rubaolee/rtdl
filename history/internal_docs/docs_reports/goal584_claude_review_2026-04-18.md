# Goal584: Adaptive Backend Engine — Claude Review

**Verdict: ACCEPT**

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6)

---

## Summary

The `run_adaptive` proposal is a coherent next backend line for the RTDL
18-workload matrix. It is approved to proceed to Goal585.

---

## Evaluation

### Coherence with the existing backend line

ACCEPT. The codebase already has five vendor RT backends (Embree, OptiX,
Vulkan, HIPRT, Apple RT), all adapted to the 18-workload matrix through
encoding shims. The proposal correctly identifies that several RTDL workload
families — DB aggregation (`conjunctive_scan`, `grouped_count`,
`grouped_sum`), graph traversal (`bfs_discover`, `triangle_match`), and 2D
geometry — are poor fits for vendor BVH ray-query encodings. A CPU-native
workload-dispatching backend with per-family kernels is a legitimate orthogonal
line, not a duplication.

The naming (`run_adaptive` as placeholder) is fine for Goal585 but should be
resolved to a stable public API name before Goal591 locks the surface.

### Scope honesty

ACCEPT. Non-goals are explicit and correct: not a DBMS, not a renderer, not a
replacement for the vendor backends, no premature performance win claims. The
risk register names the right risks (some workloads may not outperform mature
backends; compatibility dispatcher alone is not a performance backend). The
requirement that every workload must have either a native implementation with
evidence or a documented 2+ AI consensus blocker is the correct completion
criterion.

### Performance rationale

ACCEPT with note. The per-family techniques are well-grounded:

- Branchless predicate masks and sorted inputs for 2D geometry and DB scans —
  appropriate, these are branch-heavy in the existing CPU reference.
- SoA layouts and L1/L2-tiled batches for ray/triangle and NN — appropriate,
  matches the access patterns.
- CSR + frontier/visited bitsets for graph — appropriate, this is standard for
  memory-bound BFS.
- Columnar layout and hash-slot aggregation for DB — appropriate.

The rationale is speculative until measured, which the proposal acknowledges.
One gap: thread safety and memory allocation strategy for SIMD CPU kernels are
not addressed. These should be resolved in Goal585 before adding native paths
in Goal586+.

### Implementation sequencing

ACCEPT. The sequence is logical:

1. Goal585 skeleton with compatibility dispatch and explicit mode visibility —
   correct first step; preserves testability before any native kernel exists.
2. Goal586 ray/triangle native first — correct priority; this is the workload
   with the clearest comparison target (Embree, Apple RT, HIPRT).
3. Goal587–590 in workload-family order — reasonable grouping.
4. Goal591 full-matrix benchmark and honest audit — correct final gate.

The requirement that Goal585 documents which paths are native vs. compatibility
is critical and correctly stated.

---

## Minor Issues

- `run_adaptive` API name is a placeholder; plan to resolve before Goal591.
- Thread safety and memory allocation strategy for CPU SIMD paths should be
  scoped in Goal585.
- `ray_triangle_closest_hit` appears in Apple RT's native predicate set; Goal586
  should explicitly compare against it on macOS to avoid silent regression.

---

## Decision

Proceed to Goal585. No blocking issues.
