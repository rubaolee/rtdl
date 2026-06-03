# Handoff: Gemini Review for Post-Claude RayJoin Reuse Chain

Date: 2026-06-03

Please perform an independent read-only review of the post-Claude follow-up
work and write the review to:

`docs/reviews/goal3209_gemini_review_post_claude_rayjoin_reuse_chain_2026-06-03.md`

## Scope

Review Goals 3203, 3204, 3205, 3206, 3207, and 3208:

- Count-only timing with validation separated.
- Reusable Python prepared handle for repeated right-side scene reuse.
- Packed-left Python app-layer route for repeated left-query reuse.
- Intake of Claude Goal3202 findings.

## Files to Inspect

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `src/rtdsl/optix_runtime.py`
- `docs/reports/goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.md`
- `docs/reports/goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.md`
- `docs/reports/goal3206_claude_review_intake_compact_grouped_count_chain_2026-06-03.md`
- `docs/reports/goal3208_rayjoin_packed_left_compact_route_timing_2026-06-03.md`
- The matching JSON artifacts for Goals 3203, 3205, and 3208.
- Tests: `tests/goal3203_*`, `tests/goal3204_*`, `tests/goal3205_*`,
  `tests/goal3206_*`, `tests/goal3208_*`.

## Review Questions

1. Did Goal3203 close Claude's `include_rows=False` timing gap without
   overclaiming?
2. Do Goals 3204/3207 keep prepared-right and packed-left reuse in the Python
   app layer while still calling generic native/runtime primitives?
3. Do Goals 3205 and 3208 support the stated timing progression:
   one-shot count-only -> prepared-right reuse -> prepared-right plus
   packed-left reuse?
4. Did Goal3206 correctly intake Claude's L1-L4 findings, including the
   runtime metadata/docstring clarifications?
5. Are there claim-boundary leaks, stale release flags, app-specific native
   symbols, or missing tests that should be fixed before the next native
   candidate-producer optimization?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

This review must not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, or RayJoin paper reproduction claims.
