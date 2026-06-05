# External Review Handoff: Goal3438 Spatial RayJoin Prepared Subroute Reuse

Please perform an independent read-only review of latest `main` after Goal3438.

## Scope

Review the new Spatial RayJoin prepared/repeated subroute work:

- `PreparedRayJoinOptixShapePairActiveCount`
- `prepare_rayjoin_optix_shape_pair_active_count(...)`
- `pack_rayjoin_optix_shape_pair_active_count_left_shapes(...)`
- CLI route `prepared_optix_shape_pair_active_count`
- `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py`
- Goal3438 report and pod artifact.

Primary files:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py`
- `tests/goal3438_spatial_rayjoin_prepared_subroute_reuse_test.py`
- `tests/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test.py`
- `docs/reports/goal3438_spatial_rayjoin_prepared_subroute_reuse_2026-06-05.md`
- `docs/reports/goal3438_spatial_rayjoin_prepared_subroute_reuse_pod_2026-06-05.json`
- `docs/reports/goal3438_spatial_rayjoin_prepared_subroute_reuse_pod_2026-06-05.stdout`

## Questions

1. Does the overlay-seed reusable prepared handle stay app-layer and generic-engine-safe, using only generic prepared shape-pair relation/active-count semantics?
2. Does the CLI/API documentation make the boundary clear: overlay-seed scalar active count is supported, but full overlay row continuation remains unsolved?
3. Is the pod artifact coherent? Expected routes: `pip`, `lsi_dense_count`, `overlay_active_count`; 4 iterations; stable row counts; all top-level claim flags false.
4. Are the timing interpretations honest? Expected: PIP warm CuPy refine about 1.4-1.5 ms, LSI dense count about 2.5 ms median after cold first run, overlay active-count stable around 0.148 s on the available county-vs-county-slice input.
5. Did the Goal3435 review cleanup land correctly: refiner reference dropped on close and candidate row counts asserted?
6. Any bugs, missing tests, overclaims, or wording risks before the next v2.8 step?

## Required Output Paths

Claude:

- `docs/reviews/goal3439_claude_review_goal3438_spatial_rayjoin_prepared_subroute_reuse_2026-06-05.md`

Gemini:

- `docs/reviews/goal3440_gemini_review_goal3438_spatial_rayjoin_prepared_subroute_reuse_2026-06-05.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source code. If you find a bug, record it with file/line evidence
and required-before-next-step guidance.
