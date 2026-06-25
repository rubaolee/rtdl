# Call For Review: `goal4618` Point-Group Completion

Date: 2026-06-24
Author: Codex
Status: post-patch completion review request

## Goal

`goal4618` decides and executes the measured-catalog promotion for:

- `v4_point_group_nearest_witness_2d_device_arrays`

Generic primitive:

- `POINT_GROUP_NEAREST_WITNESS_2D`

This is a generic Tier-2 fused operator. It is not an app-specific kernel and
does not authorize V4 release, broad speedup wording, or public true-zero-copy
wording.

## External Pre-Patch Authorization

Claude decision:

- `future/v4/reviews/claude_v4_goal4618_point_group_promotion_decision_review_2026-06-24.raw.md`
- verdict: `authorize_point_group_promotion_patch`

Antigravity decision:

- `future/v4/reviews/antigravity_v4_goal4618_point_group_promotion_decision_review_2026-06-24.raw.md`
- verdict: `authorize_point_group_promotion_patch`

## Patch Applied

The atomic promotion patch made point-group nearest-witness measured for Torch
CUDA only.

Changed surfaces:

- measured surfaces: 4 -> 5
- candidate surfaces: 1 -> 0

Touched implementation paths:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_point_group.py`
- `src/rtdsl/v4.py`
- `scripts/v4_catalog_regression_gate.py`
- `scripts/v4_point_group_nearest_witness_device_outputs_validation.py`
- `future/v4/examples/point_group_nearest_witness_torch_device_arrays.py`

Touched validation/doc paths:

- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_point_group_device_array_api_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_point_group_nearest_witness_device_outputs_validation_test.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/point_group_device_array_frontdoor.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`

## Scope Now Recorded In Catalog

The measured catalog entry records:

- `measured_partners: ("torch",)`
- `declared_unmeasured_partners: ("cupy",)`
- `validated_optix_abi: "8.0"`
- `validated_gpu_family: "RTX A5000 / Ampere"`
- `validated_driver: "570.195.03"`
- `validated_partner_scope: "torch 2.8.0+cu128"`
- `distance_precision: "float32_computed_float64_output"`
- `prepared_search_groups: "rtdl_owned_native_scene"`
- `optix_9_1_validated: False`

The live Torch claim boundary was spot-checked and contains no `candidate`
string:

- `measured_partner: true`
- `measured_partners: ("torch",)`
- `partner_claim_status: "measured_on_v4_goal4618_pod_optix8"`
- `true_zero_copy_authorized: false`
- `contains_candidate: false`

## Evidence Before Patch

Original point-group POD evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`

Goal4618 mixed6 POD evidence:

- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.md`

Mixed6 result:

| query_count | fixture | parity | legacy-host / device-output median ratio |
| ---: | --- | --- | ---: |
| 32,768 | mixed6 | pass | 509.390582x |
| 131,072 | mixed6 | pass | 1863.096663x |

These are same-contract operator comparisons against the older host-row route.
They are not broad V4 or whole-application speedup claims.

## Post-Patch Validation

Local unit tests:

```text
py -3 -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_scope_gate_test tests.v4_release_candidate_packet_test tests.v4_catalog_regression_gate_test tests.v4_point_group_nearest_witness_device_outputs_validation_test
```

Result:

```text
Ran 35 tests in 8.653s
OK
```

Local dry-run catalog gate:

- `future/v4/evidence/v4_goal4618_catalog_dry_run_after_point_group_promotion_2026-06-24.json`
- `future/v4/evidence/v4_goal4618_catalog_dry_run_after_point_group_promotion_2026-06-24.md`

Result:

- `status: passed`
- `mode: dry-run`
- `measured_surface_count: 5`
- `candidate_surface_count: 0`
- point-group status: `dry_run`
- no forbidden claim flags

POD GPU catalog gate:

- `future/v4/evidence/v4_goal4618_catalog_gpu_after_point_group_promotion_32768_2026-06-24.json`
- `future/v4/evidence/v4_goal4618_catalog_gpu_after_point_group_promotion_32768_2026-06-24.md`

Result:

- `status: passed`
- `mode: gpu`
- examples: 9
- `include_candidates: false`
- point-group status: `measured`
- point-group correctness: `true`
- point-group `true_zero_copy_authorized: false`
- frontdoor quickstart: `measured_surface_count: 5`, `candidate_surface_count: 0`
- operator-callback planner gate still passes

## Claim Boundaries Preserved

The patch preserves:

- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`
- `true_zero_copy_authorized: false`
- CuPy performance remains unauthorized
- OptiX 9.1 remains unvalidated
- no C ABI / embedding / non-Python host claim
- no app-specific native kernel claim

## Questions For Reviewers

1. Does the patch correctly implement the pre-patch authorization?
2. Are Claude's M-1 and M-2 concerns closed by the post-patch gate and live
   claim-boundary spot-check?
3. Does the post-patch GPU catalog gate satisfy the measured-catalog gate?
4. Is the OptiX 8.0 / float32-distance / RTDL-owned-prepared-search scope
   visible enough in code/docs?
5. Is there any claim-status drift, release drift, true-zero-copy drift, or
   app-specific-kernel drift?
6. May `goal4618` be marked complete and may Codex begin `goal4619`?

## Non-Authorization

This packet does not authorize:

- V4 release
- broad V4 speedup wording
- whole-app speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- C ABI / embedding / non-Python host work
- app-specific native kernels
- CuPy performance claims
- OptiX 9.1 scope

