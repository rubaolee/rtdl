# Handoff: Gemini Review For Goal2163 Prepared OptiX LSI Build Reuse

Please perform an independent read-only review of Goal2163.

## Context

Goal2161 showed that a CuPy CUDA-core brute-force LSI backend beat one-shot RTDL/OptiX on bounded public CDB RayJoin LSI slices.

Goal2163 adds a generic prepared OptiX segment-pair-intersection surface:

- `rtdl_optix_prepare_segment_pair_intersection`
- `rtdl_optix_run_prepared_segment_pair_intersection`
- `rtdl_optix_destroy_prepared_segment_pair_intersection`

The design intentionally reuses build-side segment geometry and GAS across query launches. It must remain app-agnostic and must not introduce RayJoin-specific native engine logic.

## Files To Review

- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `tests/goal2163_optix_prepared_lsi_surface_test.py`
- `docs/reports/goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md`
- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count192_pod_2026-05-16.json`
- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count256_pod_2026-05-16.json`
- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count384_pod_2026-05-16.json`
- `tests/goal2163_prepared_optix_lsi_build_reuse_test.py`

## Review Questions

1. Does the prepared OptiX surface stay generic and app-agnostic?
2. Do the pod artifacts support the report's exact claims?
3. Is the comparison against CuPy correctly bounded as a same-runner non-RT CUDA-core baseline?
4. Are the claim boundaries conservative enough, especially around broad RT speedup and v2.0 release readiness?
5. Are there implementation or evidence debts that should block using Goal2163 as a v2.0 performance-design improvement?

## Required Output

Write your review to:

`docs/reviews/goal2164_gemini_review_goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state explicitly that this is an independent Gemini review distinct from Codex authoring, and that it does not by itself authorize v2.0 release.
