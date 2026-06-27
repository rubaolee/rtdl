# Handoff: Goal2173 Prepared OptiX Shape-Pair Relation Review

Please perform an independent Gemini review of Goal2173 and write the review to:

`docs/reviews/goal2174_gemini_review_goal2173_prepared_optix_shape_pair_relation_2026-05-16.md`

## Files To Read

- `docs/reports/goal2173_prepared_optix_shape_pair_relation_2026-05-16.md`
- `docs/reports/goal2173_prepared_overlay_seed_pod_2026-05-16.json`
- `tests/goal2173_prepared_optix_shape_pair_relation_evidence_test.py`
- `tests/goal2173_optix_prepared_shape_pair_relation_surface_test.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`

## Review Questions

1. Verify that the prepared shape-pair relation surface is generic and app-agnostic:
   - `rtdl_optix_prepare_shape_pair_relation_flags`
   - `rtdl_optix_run_prepared_shape_pair_relation_flags`
   - `rtdl_optix_destroy_prepared_shape_pair_relation_flags`
2. Verify the pod artifact numbers:
   - Embree median: `0.021841061301529408`
   - one-shot OptiX median: `0.0248165475204587`
   - prepared OptiX median: `0.019190984778106213`
   - prepared setup time: `0.009707760997116566`
   - rows: `14036`
   - commit: `7ab56c1fe382c58f2500ce7aed98696c065d9323`
3. Verify that parity is preserved across Embree, one-shot OptiX, and prepared OptiX.
4. Verify that the report does not overclaim:
   - no full RayJoin paper reproduction
   - no broad RT-core speedup
   - no v2.0 release authorization
   - no claim against stronger CUDA/CuPy spatial-prefilter baselines
5. Judge whether the interpretation is reasonable: prepared build-side state is a required RTDL v2 design pattern for RayJoin-style workloads.

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is performance/public-claim-adjacent work, so please be conservative.
