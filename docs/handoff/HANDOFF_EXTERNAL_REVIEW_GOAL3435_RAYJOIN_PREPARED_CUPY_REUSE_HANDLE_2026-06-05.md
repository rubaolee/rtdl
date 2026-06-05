# External Review Handoff: Goal3435 RayJoin Prepared CuPy Reuse Handle

Please perform an independent read-only review of latest `main` after Goal3435.

## Scope

Review the app-facing reusable prepared handle for the Spatial RayJoin PIP route:

- `PreparedRayJoinOptixCupyRefinedPip`
- `prepare_rayjoin_optix_cupy_refined_pip(...)`
- `scripts/goal3435_spatial_rayjoin_prepared_cupy_pip_reuse_handle_probe.py`
- Goal3435 report and pod artifact.

Primary files:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `scripts/goal3435_spatial_rayjoin_prepared_cupy_pip_reuse_handle_probe.py`
- `tests/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test.py`
- `docs/reports/goal3435_spatial_rayjoin_prepared_cupy_pip_reuse_handle_2026-06-05.md`
- `docs/reports/goal3435_spatial_rayjoin_prepared_cupy_pip_reuse_handle_pod_2026-06-05.json`
- `docs/reports/goal3435_spatial_rayjoin_prepared_cupy_pip_reuse_handle_pod_2026-06-05.stdout`

## Questions

1. Does the reusable handle expose the prepared/repeated-query shape honestly, without hidden partner dispatch and without moving RayJoin/CDB policy into the native engine?
2. Does it preserve the one-shot CLI route semantics while marking one-shot calls as `prepare_paid_in_call: true` and direct handle calls as reusable?
3. Is the pod artifact coherent? Expected: 4 iterations, row counts all `47262`, candidate counts all `47570`, all runs use `prepared_reuse.enabled: true`, all runs use instance identity columns, all claim flags false.
4. Are the timing interpretations honest? In particular, cold first iteration is slower; warmed prepared CuPy refine is about 1.5-2.2 ms, while candidate traversal still varies.
5. Any bugs, missing tests, overclaims, or wording risks before the next v2.8 step?

## Required Output Paths

Claude:

- `docs/reviews/goal3436_claude_review_goal3435_rayjoin_prepared_cupy_reuse_handle_2026-06-05.md`

Gemini:

- `docs/reviews/goal3437_gemini_review_goal3435_rayjoin_prepared_cupy_reuse_handle_2026-06-05.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source code. If you find a bug, record it with file/line evidence and required-before-next-step guidance.
