# Goal 550 Segment Intersection — External AI Review

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external AI review)
Verdict: **ACCEPT**

## Summary

The implementation is correct and complete for the stated scope. All blockers are absent; one advisory note is included.

## Evidence reviewed

- `docs/reports/goal550_hiprt_segment_intersection_2026-04-18.md`
- `src/native/rtdl_hiprt.cpp` — `run_lsi_2d`, `RtdlLsi2DKernel`, `intersectRtdlSegment2D`, `encode_segment_aabbs`
- `src/rtdsl/hiprt_runtime.py` — `segment_intersection_hiprt`, `run_hiprt`, `_validate_hiprt_kernel`
- `tests/goal550_hiprt_segment_intersection_test.py`
- `docs/reports/goal550_hiprt_correctness_matrix_linux_2026-04-18.json`

## What is correct

**Intersection math.** `intersectRtdlSegment2D` implements the standard 2D parametric line-segment intersection predicate. The cross-product denominator guard (`fabsf(denom) < 1e-7f`) correctly rejects parallel/nearly-parallel pairs. Both `t` and `u` parameters are checked in `[0, 1]`. The intersection point is reconstructed as `left_origin + t * left_dir`, matching the CPU reference.

**Memory safety.** Output buffer is pre-allocated at `left_count * right_count` capacity. The per-thread write index `index * right_count + count` is safe because HIPRT AABB traversal visits each primitive at most once, so `count` cannot exceed `right_count`. The host-side compaction further caps at `min(counts[i], right_count)`. Input pointer null-checks and overflow guards are present.

**Resource management.** `hiprtDestroyGeometry` and `hiprtDestroyFuncTable` are called in both normal and exception paths. `rtdl_hiprt_free_rows` is called in a `finally` block on the Python side.

**ctypes bindings.** `_RtdlSegment` (no `_pack_=1` needed, naturally aligned) and `_RtdlLsiRow` field order and types match the C structs exactly.

**Test coverage.** Three GPU tests covering: direct helper vs CPU reference, `run_hiprt` end-to-end vs CPU reference, and empty-input edge cases. All 27 Linux tests pass. Correctness matrix shows `segment_intersection` PASS with CPU/HIPRT row count parity.

**Sort stability.** `sort_lsi_rows_by_input_order` uses input-order positions so output ordering is deterministic regardless of GPU traversal order.

## Advisory (non-blocking)

**Degenerate AABBs for axis-aligned segments.** `encode_segment_aabbs` only adds `z_eps` padding in the Z dimension; it adds no padding in X or Y. A perfectly horizontal segment (y0 == y1) produces a zero-height AABB; a perfectly vertical segment (x0 == x1) produces a zero-width AABB. HIPRT may conservatively miss such primitives in the AABB traversal phase, suppressing valid intersections. The existing test includes a vertical right segment (id=2, x=1.0) and the test passes, so HIPRT on the GTX 1070 CUDA path handles this case. However, behavior may differ on AMD or in degenerate near-collinear cases at scale. Since the predicate is declared `exact=False` this is within contract, but callers working with grids or rectilinear networks should be aware.

## Verdict

ACCEPT. The implementation is a real HIPRT traversal-backed path with correct intersection math, safe buffer management, verified Linux GPU correctness, and honest scope documentation. No blockers found.
