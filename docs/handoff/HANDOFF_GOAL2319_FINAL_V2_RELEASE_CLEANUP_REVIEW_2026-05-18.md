# Handoff: Goal2319 Final v2.0 Release Cleanup Review

Please review the current RTDL `main` checkout as a v2.0 final-release cleanup
packet. This is a release-governance review, not a request to publish or tag.

## Required Output

Write exactly one review file:

- Claude: `docs/reviews/goal2320_claude_final_v2_0_release_cleanup_review_2026-05-18.md`
- Gemini: `docs/reviews/goal2321_gemini_final_v2_0_release_cleanup_review_2026-05-18.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

## Primary Artifacts To Read

- `docs/reports/goal2319_v2_0_final_cleanup_release_candidate_2026-05-18.md`
- `docs/reports/goal2068_final_v2_0_release_matrix.json`
- `docs/reports/goal2069_v2_0_pre_release_gate.json`
- `docs/reports/goal2072_v2_0_final_readiness_aggregator.json`
- `docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json`
- `docs/reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md`
- `docs/reports/goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md`
- `docs/reports/goal2318_rayjoin_v2_0_closure_and_release_prep_2ai_consensus_2026-05-17.md`

## Things To Verify

1. The native strict scan position is correctly represented: 9 uppercase
   `RTDL_DB_*` false-positive constants, 0 real app-shaped `rtdl_...` symbols.
2. The remaining OptiX diagnostic/profile environment strings no longer use
   `RTDL_OPTIX_PIP_*` or `rtdl_optix_pip_profile` wording.
3. Goal2068 now reflects the post-streaming witness evidence: no mixed rows,
   all 16 current OptiX/RT rows below 1.0 v2/v1.8 under documented contracts.
4. Goal2069 is a green engineering pre-release gate, not release
   authorization.
5. Goal2072 correctly remains blocked until current-head Claude+Gemini reviews
   and final 3-AI consensus exist.
6. Public claim boundaries remain intact: no package-install, no arbitrary
   PyTorch/CuPy acceleration, no broad RT-core speedup, no whole-app speedup,
   no arbitrary polygon overlay, no RTDL-beats-RayJoin claim.
7. v2.1+ tuning debt is correctly deferred and is not being used to block v2.0.

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2319_v2_0_final_cleanup_release_candidate_test tests.goal2068_final_v2_0_release_matrix_test tests.goal2069_v2_0_pre_release_gate_test tests.goal2072_v2_0_final_readiness_aggregator_test tests.goal1680_current_native_app_leakage_gap_test
```

## Boundary

If you accept, please state whether acceptance is `accept` or
`accept-with-boundary` and explicitly name the boundaries. Do not claim v2.0 is
released; this review is only one input to the required final 3-AI consensus.
