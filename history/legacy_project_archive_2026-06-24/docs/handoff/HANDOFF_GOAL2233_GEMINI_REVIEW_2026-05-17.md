# Handoff: Goal2233 Gemini Review

Please perform an independent Gemini review of Goal2233 and write the result to:

`docs/reviews/goal2234_gemini_review_goal2233_prepared_ray_segment_group_count_2026-05-17.md`

Read these files:

- `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md`
- `tests/goal2233_prepared_ray_segment_group_count_test.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`

Review requirements:

1. Confirm whether the prepared ray/segment group-count API remains app-agnostic.
2. Confirm whether the prepared-scene reuse design correctly addresses repeated segment-scene construction without overclaiming RayJoin/PIP speedups.
3. Check the report's negative performance conclusion: 10k RayJoin-style probe parity matched, unprepared median 1.476056s, prepared median 0.820912s, legacy optimized PIP median 0.039768s, prepared path still 20.64x slower.
4. Verify that the boundary is honest: no v2.0 release claim, no whole-app speedup claim, no device-resident grouped reduction claim.
5. State clearly that this is an independent Gemini review distinct from Codex.

Use one of the accepted verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`, because the implementation is correct and useful as a prepared generic primitive, but the performance evidence says the next optimization must change the grouped-output contract.
