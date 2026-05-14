# Goal1865 - Road Hazard Partner Priority Flags

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1865 adds the next narrow v2.0 app-lift:

`rtdsl.road_hazard_priority_flags_optix_partner_device_columns(...)`

The adapter reuses the Goal1861 segment/polygon hit-count device-column path,
then applies the road-hazard priority threshold with the selected partner tensor
library. It returns partner-owned columns:

- `road_ids`
- `hit_counts`
- `priority_flags`

The native engine still sees only the generic ray/primitive candidate-witness
contract. No road, hazard, segment, polygon, or priority semantic is added to
the native OptiX ABI.

## Contract

The intended metadata boundary is:

- `adapter: road_hazard_priority_flags_optix_partner_device_columns`
- `app: road_hazard_screening`
- `input_contract: caller_supplied_partner_device_columns`
- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_count_materialization: partner_columns_from_host_exact_filter`
- `app_priority_materialization: partner_gpu_threshold_from_hit_counts`
- `app_priority_host_materialization: false`
- `whole_app_true_zero_copy_authorized: false`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## Why This Is The Right Next Slice

`road_hazard_screening` is already a hit-count-threshold application. Lifting it
through the partner count-column path grows v2.0 app coverage without inventing a
new native primitive and without reopening the generic engine boundary.

This does not finish the app matrix. It proves that one more public app can be
expressed as Python+partner orchestration over the generic candidate-witness
slice. Goal2000 supersedes the older stronger zero-copy wording: exact
segment/polygon hit-count semantics currently require an app-side exact filter
before the priority threshold can run in partner columns.

## Boundary

This is local contract evidence only. No pod timing was run for this goal.

The goal does not authorize v2.0 release wording, broad RT-core speedup wording,
whole-application acceleration wording, or an all-app v2.0-vs-v1.8 performance
table.

## Extra Review

GitHub Copilot CLI reviewed this goal as an extra GPT-backed reviewer in
`docs/reviews/goal1866_copilot_extra_review_goal1865_road_hazard_partner_priority_flags_2026-05-13.md`
with verdict `accept-with-boundary`.

That review does not replace Claude or Gemini for strict distinct-AI consensus.
