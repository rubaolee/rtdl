# Goal4511 / V3 M115 Triangle Counting Clean-Target Audit

## Conclusion

Triangle Counting is closed as an internal V3 clean target. RTDL now completes the three former-OOM large paper rows exactly with generic ray/triangle weighted-summary primitives and partner-side graph lowering. The current internal route is the Goal4479 numba_direct_sort_rle prepared segment replay path, while the formal external comparison remains Goal4475/M78. The honest public boundary is unchanged: do not claim RTDL beats cuGraph, authors pure kernels, or public RT-core triangle-count speedups.

## Formal External Comparison

RTDL M78 is exact and much faster than the authors full pipeline on completed rows, but cuGraph remains faster end to end and authors pure count kernels remain faster than RTDL query/native traversal. This packet is the formal external comparison baseline, not a public RT-core speedup claim.

| Dataset | RTDL M78 total | cuGraph faster | RTDL vs M71 | Author pure-kernel reading |
| --- | ---: | ---: | ---: | --- |
| com-lj | 5.404s | 3.15x | 2.62x | RTDL query 2.46x slower than author rt count |
| soc-LiveJournal1 | 11.669s | 4.91x | 2.21x | RTDL query 2.56x slower than author rt count |
| com-orkut | 35.379s | 4.89x | 3.25x | failed_sigkill_after_149151_ms |

## Current Internal Route

`unique_weighted segmented RT-2A1 + numba_direct_sort_rle unique/count + prepared_segment_replay + generic prepared ray-batch weighted any-hit sum`

| Dataset | Baseline total | Sort/RLE total | Total speedup | Segment-build speedup |
| --- | ---: | ---: | ---: | ---: |
| com-lj | 7.308s | 6.489s | 1.13x | 1.14x |
| soc-LiveJournal1 | 14.467s | 13.273s | 1.09x | 1.15x |
| com-orkut | 38.564s | 35.990s | 1.07x | 1.19x |

## Local-Hash Decision

| Dataset | 2,048-row coverage | 16,384-row coverage | Prototype speedup | Integrated backend ratio | Integrated segment-build ratio | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| com_lj | 64.77% | 93.73% | 1.13x | 0.83x | 0.69x | `reject_hybrid_candidate` |
| soc_livejournal1 | 53.87% | 89.85% | 1.01x | 0.38x | 0.19x | `reject_hybrid_candidate` |
| com_orkut | 21.21% | 69.43% | 1.43x | 0.95x | 0.87x | `reject_hybrid_candidate` |

The local-hash branch is not dismissed because the idea is invalid. It is dismissed because the integrated route regresses backend and segment-ray build on all three paper rows. `com_orkut` has a slightly better integrated total in the M98 packet, but it fails the route-promotion gate because the hot materialization phases got worse.

## M113 Applicability

- Current route should use M113: `False`.
- Reason: Triangle Counting already uses a generic prepared ray-batch weighted any-hit primitive inside graph-derived segments. The current bottleneck is segment unique/count materialization and per-segment launch/envelope work, not a missing prepared graph chunk executor contract.
- Future use: A future coarser-batched segmented unique/count reduction or prepared replay executor may reuse the M113 discipline if it really has contiguous prepared chunks, per-chunk handles, and explicit partner continuation.

## Closed

- All three large former-OOM paper rows complete exactly under RTDL's generic ray/triangle weighted-summary route.
- Current internal route is Goal4479 `numba_direct_sort_rle`, not the rejected local-hash hybrid.
- CuPy/Numba partner roles are evidence-bounded and explicit; there is no hidden automatic partner selection.
- App-specific native engine callbacks remain disallowed.

## Still Blocked

- Public RT-core triangle-count speedup wording.
- RTDL-beats-cuGraph wording.
- RTDL-beats-authors-pure-kernel wording.
- Treating M113 as the current Triangle Counting performance path.
