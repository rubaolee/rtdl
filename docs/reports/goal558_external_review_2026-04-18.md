# External Review: Goal 558 HIPRT `triangle_match`

Date: 2026-04-18
Reviewer: Claude (Sonnet 4.6)

## Verdict

**ACCEPT.** The implementation is complete, consistent with the report, and passes the honesty boundary test. No fabricated evidence found.

## Evidence Verified

| Claim | Status |
|---|---|
| Native `rtdl_hiprt_run_triangle_probe` exported from `rtdl_hiprt.cpp` | Confirmed — line 4248 |
| `run_triangle_probe` internal implementation | Confirmed — lines 3622–3781 |
| `RtdlTriangleProbeKernel` device kernel | Confirmed — embedded string literal, line 1627 |
| `intersectRtdlTriangleGraphEdgeBySource` custom intersector | Confirmed — embedded string literal, line 1607 |
| `triangle_match_hiprt` Python binding | Confirmed — `hiprt_runtime.py:1206` |
| `triangle_match_hiprt` exported from `rtdsl.__init__` | Confirmed — lines 103, 566 |
| Test file with 4 HIPRT-guarded tests | Confirmed — `tests/goal558_hiprt_triangle_match_test.py` |
| Linux matrix JSON `triangle_match` PASS, `parity=true` | Confirmed — `goal558_hiprt_correctness_matrix_linux_2026-04-18.json` |
| Matrix summary `pass=15, fail=0, not_implemented=3` | Confirmed |

## Architecture Notes

The implementation matches the report's description:

- Graph edges are encoded as source-keyed AABB-list custom primitives via `encode_graph_edge_source_aabbs`.
- Rays are fired with origin `(u, 0, -1)` per seed; the kernel filters AABB hits by `edge.src == u` in-kernel.
- The `v -> w` edge check is done on-device via `hasGraphEdge` (CSR linear scan).
- Host-side sort by `(seed_index, w, u, v)` matches the CPU reference contract.
- `unique=True` deduplication is O(n²) via `std::any_of` — correct for small graphs, slow at scale, but covered by the honesty boundary.

### One Wording Imprecision

The report states that `intersectRtdlTriangleGraphEdgeBySource` "traverses one side of each seed edge." In practice, this function is a trivially-accepting stub (`hit.t = 0.0f; return true` — always accepts all AABB hits). The actual source-match filter (`edge.src != u`) is in `RtdlTriangleProbeKernel`, not in the intersector. This is a valid HIPRT custom-intersector pattern (the intersector cannot receive query context), but the description slightly misattributes where the filtering occurs. This is a documentation imprecision, not a functional defect.

### Single-Thread Execution

The kernel is launched 1×1×1 / 1×1×1. This is deterministic and correct but provides no GPU parallelism. The report's honesty boundary explicitly discloses this ("one device thread for deterministic bounded semantics"). Acceptable for v0.9 correctness-first scope.

## Correctness

Tests cover: direct helper parity, `run_hiprt` dispatch parity, `unique=False` with duplicate seeds, and empty-input cases. All 4 tests are `@unittest.skipUnless(hiprt_available(), ...)` guarded — no false positives on non-HIPRT hosts. Linux HIPRT run shows 16 tests in ~20s, all passing.

## Summary

Goal 558 is a complete, honest, bounded HIPRT `triangle_match` backend. It advances the v0.9 HIPRT matrix from 14 to 15 passing workloads without CPU fallback. The single identified wording imprecision (source-match attribution) does not affect correctness or honesty. Recommend accept as-is.
