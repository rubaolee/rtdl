# Handoff: Claude Review for Goal3218 RayJoin Public LSI Dense Probe

Date: 2026-06-03

Please perform an independent review and write the result to:

`docs/reviews/goal3219_claude_review_goal3218_rayjoin_public_lsi_dense_probe_2026-06-03.md`

## Scope

Review Goal3218, which follows the Goal3214/3217 review chain by adding
bounded public RayJoin-style CDB evidence for the fused dense segment-pair
left-id count route.

## Files to Inspect

- `scripts/goal3218_rayjoin_public_lsi_dense_count_probe.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `docs/reports/goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.md`
- `docs/reports/goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.json`
- `tests/goal3207_packed_left_rayjoin_compact_route_test.py`
- `tests/goal3218_rayjoin_public_lsi_dense_count_probe_test.py`
- `tests/goal3218_rayjoin_public_lsi_dense_count_probe_artifact_test.py`
- Prior context:
  - `docs/reviews/goal3214_claude_review_fused_segment_pair_count_chain_2026-06-03.md`
  - `docs/reviews/goal3217_gemini_review_post_claude_fused_count_hardening_2026-06-03.md`

## Review Questions

1. Does Goal3218 correctly reuse public RayJoin-style CDB slice materialization
   instead of only authored synthetic all-crossing fixtures?
2. Does the probe compare the previous compact route and the new dense route
   fairly under the same prepared-right and packed-left setup?
3. Does the canonical `Segment` normalization fix belong in the Python app layer
   and preserve the app-agnostic native boundary?
4. Does the artifact contain enough hardware metadata to address the prior
   reproducibility gap for internal evidence?
5. Are the dense-vs-compact ratios and count matches interpreted correctly
   without public speedup, RT-core, release, zero-copy, or RayJoin-paper claims?
6. What remains before stronger RayJoin-vs-RayJoin or public benchmark claims?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Do not authorize release, public speedup claims, broad RT-core claims, true
zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin paper-reproduction
claims.

