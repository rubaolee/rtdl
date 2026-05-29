# Goal2684 Claude Review Response

Date: 2026-05-28

Imported external review:

- `docs/reports/external_reviews/goal2684_v2_4_v2_5_claude_critical_review_2026-05-28.docx`
- `docs/reports/external_reviews/goal2684_v2_4_v2_5_claude_critical_review_2026-05-28.md`

Reviewer verdict: `Accept with fixes`

## Summary

Claude reviewed the v2.4/v2.5 architecture and classified Goal2684 direction as
correct: RT traversal should remain in RTDL/Embree/OptiX, Triton should own
post-RT continuation, and app semantics should stay outside the engine.

The review blocked promotion on two issues:

1. The v2.5 preview gate still claimed CUDA execution had not been validated,
   even though Goal2683 validated GPU correctness on NVIDIA L4.
2. The group-id bounds contract was not explicit enough for the reference and
   Triton continuation paths.

## Actions Taken

- Split the preview gate state:
  - `V2_5_GOAL2683_CUDA_EXECUTION_VALIDATED = True`
  - `V2_5_BENCHMARK_INTEGRATION_VALIDATED = False`
- Updated `v2_5_partner_preview_gate()` so CUDA continuation correctness is
  recorded as validated while benchmark integration, RT hit-stream handoff,
  public claims, and external consensus remain gated.
- Updated `validate_v2_5_partner_preview_gate()` to require the Goal2683 CUDA
  correctness state instead of asserting the stale pre-pod state.
- Added a public group-id validation contract:
  - `V2_5_GROUP_ID_VALIDATION_CONTRACT`
  - all group-id operations now document that group ids must be in
    `[0, group_count)` and are rejected before continuation.
- Added tests that import the Goal2683 CUDA artifact and verify all recorded
  low-level correctness rows are true.
- Added tests that verify invalid group ids are rejected by the Python
  reference and, when CUDA is available, by the Triton precheck.
- Added a grouped-argmin tie-break implementation note and kept the existing
  equal-score CUDA test as the preview promotion guard.
- Added the requested commit-mismatch note to the Goal2683 report.
- Renamed the RayDB migration-plan partner label from `current_hot_path_partner`
  value `triton_adapter_front_door_for_count_sum_min_max` to
  `preview_adapter_front_door_for_count_sum_min_max` to avoid implying
  performance promotion.

## Remaining Review Items

These are still open but non-blocking for the Goal2684 implementation slice:

- Public adapter front doors for `grouped_argmin_f64` and
  `bounded_collect_finalize_i64`.
- Triton timing split between kernel time and Torch tensor-carrier compaction.
- Numba fallback coverage beyond count/sum.
- Full OptiX/Triton Goal2684 pod evidence once a CUDA-visible pod is available.
- External re-review after Goal2684 pod artifacts exist.

## Current Claim Boundary

No public speedup claim is authorized. The accepted claim is limited to:

- v2.5 CUDA continuation correctness was validated by Goal2683 artifacts;
- Goal2684 implementation direction is architecturally accepted with fixes;
- full RT+Triton performance evidence remains blocked on a working CUDA pod and
  external review of the final artifacts.
