# Handoff: Gemini Review For Goal3677

Please perform a read-only independent review of Goal3677 and write your review to:

`docs/reviews/goal3678_gemini_review_goal3677_relation_status_exact_count_2026-06-06.md`

## Files To Inspect

- `docs/reports/goal3677_relation_status_filtered_exact_count_2026-06-06.md`
- `docs/reports/goal3677_relation_status_exact_count_a5000/summary.json`
- `tests/goal3677_relation_status_filtered_exact_count_test.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/closed_shape_topology.py`

## Review Questions

1. Is the new native relation-status filtered candidate-column producer generic/app-agnostic, or does it introduce RayJoin/app-specific native logic?
2. Does the implementation correctly avoid the old raygen count-only payload accumulator and count filtered rows only where `relation_status_filter` is available?
3. Is the composed Python/Numba exact count helper honest about its contract, especially the fact that boundary-status rows are dense on this dataset and this is not the final RayJoin-level performance primitive?
4. Do the report and artifact preserve claim boundaries: no release, public speedup, RayJoin reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or default-route authorization?
5. Are the tests sufficient for this internal engineering step, and what should be required before any stronger performance or release claim?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is an internal v2.x performance-engineering step, not a release packet.
