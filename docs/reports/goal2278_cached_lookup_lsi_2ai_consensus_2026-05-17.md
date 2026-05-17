# Goal2278: Cached Lookup LSI 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers:

- Goal2275 generic cached right-side lookup for prepared segment-pair scenes.
- Goal2276 pod measurement on the RayJoin-exported 100k LSI stream.
- Goal2277 Gemini review.

## Evidence

Goal2276 measured commit `5c41ade112fb7ebbcdd6ed593eea96eb806db75f` on an
RTX A5000 pod using the same RayJoin-exported 100k LSI stream from Goal2273.

Measured improvement versus Goal2273 baseline:

| Path | Goal2273 Median Sec | Goal2276 Median Sec | Speedup |
| --- | ---: | ---: | ---: |
| Raw witness rows | 0.181889 | 0.165026 | 1.102x |
| Exact scalar count | 0.185313 | 0.159957 | 1.159x |

Parity held at `8,921` intersections.

## External Review

Gemini review:

`docs/reviews/goal2277_gemini_review_goal2275_2276_cached_lookup_2026-05-17.md`

Gemini verdict: `accept`.

Gemini confirmed:

- Goal2275 is a generic prepared-scene cache, not app-specific RayJoin/LSI
  engine logic.
- Goal2276 supports the narrow measured improvement claim only.
- The report avoids overclaiming and states that the broader LSI performance
  gap remains.

## Consensus Verdict

Codex + Gemini consensus: `accept-with-boundary`.

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream, caching the
prepared right-side segment lookup improves the exact prepared segment-pair raw
row path by about `1.10x` and the scalar-count path by about `1.16x` versus the
Goal2273 baseline implementation.

Still not allowed:

- whole RayJoin application speedup,
- RayJoin paper reproduction,
- RTDL beats RayJoin,
- broad RT-core speedup,
- true zero-copy or pure device-resident continuation.

## Next Direction

This closes an avoidable prepared-scene host metadata overhead. The remaining
LSI gap points toward generic segment-pair candidate/refinement continuation,
not app-specific engine customization.

