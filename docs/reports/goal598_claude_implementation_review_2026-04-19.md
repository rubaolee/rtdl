# Goal598: Independent Implementation Review

Date: 2026-04-19
Reviewer: Claude (Sonnet 4.6)
Verdict: **ACCEPT**

## Scope

Review of `src/native/rtdl_apple_rt.mm` (`rtdl_apple_rt_run_lsi`), `tests/goal598_apple_rt_masked_segment_intersection_test.py`, and the associated closure/performance documents.

## Correctness

**Design is sound.** Right segments are extruded into z-axis quads and packed ≤32 per chunk with one mask bit each. Each left segment fires as a single ray with the full chunk mask. Nearest-hit traversal peels one candidate per pass; the bit is cleared whether or not analytic refinement confirms the hit, preventing infinite loops on degenerate geometry. The pass loop is bounded by `chunk_count`, so termination is guaranteed.

**Ray parameterization is correct.** The ray direction is the unnormalized segment vector `(x1-x0, y1-y0, 0)` and `maxDistance = 1.000001f`, so `t=1` maps to the far endpoint. The 1e-6 epsilon preserves endpoint-touch intersections before analytic refinement trims exact bounds.

**Analytic refinement preserves RTDL exactness.** `segment_intersection_point` uses double-precision with a 1e-7 denom guard and strict `[0,1]` interval checks, ensuring float-precision RT false positives are silently dropped and do not produce spurious rows.

**Output ordering is correct.** Per-left hit lists are sorted by right-segment input index before flattening, giving the required left-major/right-input-order output.

## Tests

16/16 tests pass (including pre-existing suites). New tests cover:
- Zero-hit and one-hit parity against CPU reference
- 40 right segments forcing two chunks (>32), verifying multi-chunk accumulation
- Duplicate right segments crossing at the same point (collision at same distance)
- Left-major/right-input-order ordering

Coverage is adequate for the stated correctness goals.

## Performance

Measured on Apple M4 with 5 warmups, 20 repeats:
- Segment-intersection median: 0.0313 s vs. 0.0925 s (Goal597 pre-change) — **2.95x reduction**
- Apple RT / Embree ratio: 4.17x (down from 11.87x)
- Parity: True; Stability: True

The closure document correctly characterizes the improvement: AS-build amortization, not enumeration elimination. Apple RT remains slower than Embree for dense output. Unstable closest-hit timing is properly flagged as engineering-triage only.

## Issues

**Minor — pre-existing memory management pattern.** On error paths inside `rtdl_apple_rt_run_lsi` (e.g., return codes 5, 6 for intersection-buffer or intersector creation failure), `ray_buffer` and `intersection_buffer` are not explicitly released before return. The same pattern exists in `rtdl_apple_rt_run_ray_hitcount_3d` from Goal597. This does not affect correct operation (these are error paths only, and `@autoreleasepool` provides a safety net under ARC), but the inconsistency with the explicit-release style elsewhere is worth tracking. This is not a regression introduced by Goal598 and does not warrant blocking.

## Summary

The implementation correctly solves the stated problem, preserves RTDL row identity and CPU-reference parity, has thorough tests, and delivers a measured and honestly-documented performance improvement. No new correctness or safety issues are introduced.

**ACCEPT**
