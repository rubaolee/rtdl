# Goal3675 External Review Request

Please perform a read-only review of Goal3675 and write your review to:

`docs/reviews/goal3676_gemini_review_goal3675_boundary_contact_numba_count_2026-06-06.md`

## Files To Inspect

- `docs/reports/goal3675_boundary_contact_relation_status_numba_count_2026-06-06.md`
- `docs/reports/goal3675_rayjoin_pip_full_county_candidate_refine_timing_a5000/summary_boundary_contact_numba_count_resident_stream_diagnostic.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/closed_shape_topology.py`
- `scripts/goal3675_rayjoin_pip_full_county_candidate_refine_timing.py`
- `tests/goal3675_closed_shape_candidate_relation_status_columns_test.py`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the native engine remain app-agnostic? In particular, do the new columns expose generic relation status and boundary-element ordinal concepts rather than RayJoin/CDB/GIS policy?
2. Is the Numba continuation genuinely a user-friendly partner route for exact count-only workloads without requiring user-written CUDA strings?
3. Does the timing report correctly separate incorrect fast scalar count, one-shot exact row-stream routes, and resident-stream diagnostic timing?
4. Is the key design conclusion sound: the current blocker is stream allocation/free/materialization contract, so the next generic runtime target should be reusable native output buffers or a native exact scalar-count primitive?
5. Are the claim boundaries tight enough? The review should reject any wording that implies RayJoin reproduction, RTDL beats RayJoin, release readiness, broad RT-core speedup, default broad-CDB route, or true zero-copy.

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This request is for review only. Do not modify source code.
