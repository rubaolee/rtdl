# Goal2289: Packed-Left Direct-Index Segment-Pair Refinement

Status: accepted for the packed-left path only.

## Purpose

Goal2280 rejected direct-index segment-pair refinement for the tuple-input path:
on that path, repeated Python tuple packing dominated enough that the native
index shortcut did not produce a useful end-to-end improvement.

Goal2289 re-tests the same idea under the newer Goal2287 programming contract:
the right/build-side geometry is prepared once, the reusable left/query segment
batch is packed once, and repeated raw/count calls operate on those packed
objects. Under this contract the native exact-refinement phase is visible again,
so a direct candidate-index shortcut can be evaluated fairly.

## Implementation

The OptiX segment-pair any-hit candidate row still carries the public
`left_id`/`right_id`, but now also carries dense `left_index`/`right_index`
values for the currently packed left query batch and prepared right geometry.

Host exact refinement first uses the dense indices to recover the original
segments directly. The existing id-map lookup remains as a defensive fallback if
an index is out of range. This keeps the public Python row contract unchanged:
users still see `left_id`, `right_id`, `ix`, and `iy`.

This is generic engine plumbing. It does not add RayJoin-specific native logic,
does not change intersection semantics, and does not change the Python API.

## Same-Pod A/B Evidence

Both A/B repetitions ran on the same pod:

- SSH: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Baseline commit: `6f3bac51`
- Workload: RayJoin-exported 100k LSI query stream used by Goal2285
- Contract: prepared right geometry plus prepacked reusable left/query segment batch
- Repeats per run: 7 measured raw calls and 7 measured count calls, after 2 warmups

| Run | Baseline Raw Median (s) | Candidate Raw Median (s) | Raw Speedup | Baseline Count Median (s) | Candidate Count Median (s) | Count Speedup | Rows | Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.009887304 | 0.009029787 | 1.095x | 0.009486409 | 0.009139083 | 1.038x | 8921 | 8921 |
| 2 | 0.009843135 | 0.007861272 | 1.252x | 0.009463258 | 0.007961275 | 1.189x | 8921 | 8921 |

Phase telemetry confirms the intended mechanism:

| Run | Baseline Raw Exact-Refine Median (s) | Candidate Raw Exact-Refine Median (s) | Baseline Count Exact-Refine Median (s) | Candidate Count Exact-Refine Median (s) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.008317234 | 0.007371517 | 0.007886156 | 0.007483150 |
| 2 | 0.008262912 | 0.006340875 | 0.007870468 | 0.006457506 |

## Artifacts

- `docs/reports/goal2289_direct_index_packed_ab_run1_baseline_2026-05-17.json`
- `docs/reports/goal2289_direct_index_packed_ab_run1_candidate_2026-05-17.json`
- `docs/reports/goal2289_direct_index_packed_ab_run2_baseline_2026-05-17.json`
- `docs/reports/goal2289_direct_index_packed_ab_run2_candidate_2026-05-17.json`

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream, direct
candidate indices improve repeated prepared segment-pair calls under the
prepacked-left contract by about `1.1x` to `1.25x` for raw rows and `1.04x` to
`1.19x` for scalar count.

Not allowed:

- claim that Goal2280's tuple-input rejection is overturned;
- whole RayJoin application speedup;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- broad RT-core speedup;
- true zero-copy;
- claim that all workloads benefit from direct candidate indices.

## Verdict

Codex verdict: `accept-with-boundary`.

The optimization is worth keeping because it improves the now-recommended
packed-left v2 programming path, preserves row/count parity, and stays within
the generic segment-pair primitive. It remains a narrow subpath optimization
until externally reviewed and folded into any broader release claim.
