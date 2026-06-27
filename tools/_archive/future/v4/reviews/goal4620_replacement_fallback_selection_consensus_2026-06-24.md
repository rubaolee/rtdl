# `goal4620` Replacement Fallback Selection Consensus

Date: 2026-06-24
Author: Codex
Status: accepted with amendments; implementation may start after Amendment 1 verification

## Decision

Select `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` as the
replacement fallback candidate for `goal4620`.

This continues the already-reviewed `goal4615`-`goal4623` sequence. It does
not create a new goal number, does not reuse completed `goal4617` or
`goal4618` work as fake progress, and does not authorize measured-catalog
promotion.

## Inputs

- Candidate-selection packet:
  `future/v4/reviews/call_for_review_v4_goal4620_replacement_fallback_selection_2026-06-24.md`
- Claude review:
  `future/v4/reviews/claude_v4_goal4620_replacement_fallback_selection_review_2026-06-24.raw.md`
- Prior aggregate-tree rejection:
  `future/v4/reviews/claude_v4_goal4620_aggregate_tree_feasibility_protocol_review_2026-06-24.raw.md`
- `goal4619` completion consensus:
  `future/v4/reviews/goal4619_completion_consensus_2026-06-24.md`

## Reviewer Positions

| Seat | Position |
|---|---|
| Codex | Proposed Candidate A, `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`, with candidate status only. |
| Claude | `accept_with_required_amendments`; Candidate A accepted subject to three amendments. |
| Mill subagent | Recommended ray-triangle `hit_count_sum` / `weighted_sum` device rays, with `weighted_sum` primary because it is closest to a V4 Tier-2 device-array surface and already has a device-output graph executor path. |
| Halley subagent | Recommended the already-promoted grouped-i64 surface as strongest overall V4 surface; Codex rejects that as a `goal4620` candidate because it would double-count completed `goal4617`. |

This is sufficient to begin implementation after the explicit Claude
Amendment 1 blocker is verified. Final `goal4620` completion still requires
3-AI completion consensus or explicit review debt.

## Claude Required Amendments

1. Verify before implementation that
   `PreparedOptixStaticTriangleScene3D.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor`
   exists and returns the claimed structural metadata.
2. Add claim-boundary metadata documenting scene-preparation ownership.
3. Pin primary output scalar allocation policy. The selected policy is:
   RTDL-provided allocator/helper as primary, caller-owned output scalar as
   optional override. Metadata must record the exercised path.

## Amendment 1 Verification

Verified in `src/rtdsl/optix_runtime.py`:

- Method exists at
  `PreparedOptixStaticTriangleScene3D.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor`.
- It returns `PreparedOptixRayBatchWeightedSumDeviceOutputGraphExecutor3D`.
- The executor validates:
  - `ray_weights` as direct device pointer handoff
  - `weighted_hit_sum_out` as direct read/write device pointer handoff
  - `weighted_hit_sum_out` dtype `uint64`, shape `(1,)`, contiguous layout,
    same CUDA device as ray columns
- `launch()` structurally returns:
  - `device_output_used: True`
  - `host_scalar_read_before_consumer: False`
  - `host_row_materialization_before_consumer: False`
  - `query_rays_uploaded_each_run: False`
  - `ray_weights_uploaded_each_run: False`
  - `public_speedup_claim_authorized: False`
  - `true_zero_copy_authorized: False`
- `to_metadata()` structurally returns:
  - `device_output_used: True`
  - `host_scalar_read_before_consumer: False`
  - `host_row_materialization_before_consumer: False`
  - `query_rays_uploaded_each_run: False`
  - `ray_weights_uploaded_each_run: False`
  - `public_speedup_claim_authorized: False`

Command-level check passed for the required strings:

```text
PASS def prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor
PASS "device_output_used": True
PASS "host_scalar_read_before_consumer": False
PASS "host_row_materialization_before_consumer": False
PASS "query_rays_uploaded_each_run": False
PASS "ray_weights_uploaded_each_run": False
```

## Authorization Boundary

Implementation of the `goal4620` candidate front door may now begin.

This does not authorize:

- measured-catalog promotion
- V4 release or release-candidate status
- true-zero-copy wording
- whole-app or broad V4 speedup claims
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- app-specific native kernels
- implementation of Candidate B, C, D, or E inside `goal4620`
- marking `goal4620` complete before completion review

