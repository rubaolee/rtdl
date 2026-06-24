# Goal2291: Packed-Left Direct-Index Segment-Pair 2-AI Consensus

Status: accepted with boundary.

## Scope

Goal2291 closes the Goal2289 direct-index segment-pair evidence package. The
accepted claim is narrow: on one recorded RTX A5000 pod and one RayJoin-exported
100k LSI stream, direct candidate indices improve repeated prepared segment-pair
raw/count calls under the prepacked-left contract.

This does not overturn Goal2280. The tuple-input direct-index experiment remains
rejected because that path was dominated by repeated Python tuple packing.

## Evidence

- Implementation and pod A/B report:
  `docs/reports/goal2289_packed_left_direct_index_segment_pair_2026-05-17.md`
- A/B artifacts:
  - `docs/reports/goal2289_direct_index_packed_ab_run1_baseline_2026-05-17.json`
  - `docs/reports/goal2289_direct_index_packed_ab_run1_candidate_2026-05-17.json`
  - `docs/reports/goal2289_direct_index_packed_ab_run2_baseline_2026-05-17.json`
  - `docs/reports/goal2289_direct_index_packed_ab_run2_candidate_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2290_gemini_review_goal2289_direct_index_packed_left_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini/Antigravity verdict: `accept-with-boundary`.

The agreed interpretation is:

- the optimization preserves the public segment-pair row contract;
- the dense indices are generic candidate-row metadata, not RayJoin-specific
  logic;
- both same-pod repetitions preserve `8921` raw rows and scalar count parity;
- the measured packed-left improvements are real enough to keep:
  - run 1: `1.095x` raw rows and `1.038x` scalar count;
  - run 2: `1.252x` raw rows and `1.189x` scalar count.

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
