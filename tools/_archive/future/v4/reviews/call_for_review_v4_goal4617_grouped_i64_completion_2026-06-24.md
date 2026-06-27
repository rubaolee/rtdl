# Call For Review: `goal4617` Grouped-I64 Completion

Date: 2026-06-24
Author: Codex
Status: post-patch completion review request

## Goal

`goal4617` decides and executes the measured-catalog promotion for:

- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

Generic primitive:

- `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`

This is a generic Tier-2 fused operator. It is not an app-specific kernel and
does not authorize V4 release or broad speedup wording.

## External Pre-Patch Authorization

Claude decision:

- `future/v4/reviews/claude_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.raw.md`
- verdict: `authorize_grouped_i64_promotion_patch`

Antigravity decision:

- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_retry_2026-06-24.raw.md`
- verdict: `authorize_grouped_i64_promotion_patch`

The first Antigravity attempt returned an empty output file and is not counted:

- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.raw.md`

## Patch Applied

The atomic promotion patch made grouped-i64 measured for Torch CUDA only and
left point-group nearest-witness as the only current candidate.

Changed surfaces:

- measured surfaces: 3 -> 4
- candidate surfaces: 2 -> 1

Touched implementation paths:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4.py`
- `scripts/v4_catalog_regression_gate.py`
- `scripts/v4_primitive_grouped_i64_device_outputs_validation.py`
- `future/v4/examples/primitive_grouped_i64_reduction_torch_device_arrays.py`

Touched validation/doc paths:

- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_ray_triangle_device_array_api_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`

## Scope Now Recorded In Catalog

The measured catalog entry records:

- `measured_partners: ("torch",)`
- `declared_unmeasured_partners: ("cupy",)`
- `validated_optix_abi: "8.0"`
- `validated_gpu_family: "RTX A5000 / Ampere"`
- `validated_driver: "570.195.03"`
- `validated_partner_scope: "torch 2.8.0+cu128"`
- `optix_9_1_validated: False`

This satisfies the prior requirement that the OptiX 8.0 ceiling appear in the
catalog itself, not only in evidence/review prose.

## Evidence Before Patch

Original grouped-i64 POD evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`

Goal4617 multi-width POD evidence:

- `future/v4/evidence/v4_goal4617_grouped_i64_width1_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width16_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width256_pod_gate_32768_131072_2026-06-24.json`

Summary:

| group_width | ray_count | group_count | parity | legacy-host / device-output median ratio |
| ---: | ---: | ---: | --- | ---: |
| 1 | 32,768 | 32,768 | pass | 166.545732x |
| 1 | 131,072 | 131,072 | pass | 411.866531x |
| 16 | 32,768 | 2,048 | pass | 11.270692x |
| 16 | 131,072 | 8,192 | pass | 21.369330x |
| 256 | 32,768 | 128 | pass | 1.641351x |
| 256 | 131,072 | 512 | pass | 2.977954x |

These are same-contract operator comparisons against the older host-output
primitive. They are not broad V4 or whole-application speedup claims.

## Post-Patch Validation

Local unit tests:

```text
py -3 -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_scope_gate_test tests.v4_release_candidate_packet_test tests.v4_catalog_regression_gate_test tests.v4_point_group_nearest_witness_device_outputs_validation_test
```

Result:

```text
Ran 35 tests in 8.880s
OK
```

Python compile gate:

```text
py -3 -m py_compile src/rtdsl/v4_operator_catalog.py src/rtdsl/v4_ray_triangle.py src/rtdsl/v4.py scripts/v4_catalog_regression_gate.py scripts/v4_primitive_grouped_i64_device_outputs_validation.py future/v4/examples/primitive_grouped_i64_reduction_torch_device_arrays.py
```

Result: passed.

Local dry-run catalog gate:

- `future/v4/evidence/v4_goal4617_catalog_dry_run_after_grouped_i64_promotion_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_catalog_dry_run_after_grouped_i64_promotion_2026-06-24.md`

Result:

- `status: passed`
- `mode: dry-run`
- grouped-i64 example status: `dry_run`
- `measured_surface_count: 4`
- `candidate_surface_count: 1`

POD GPU catalog gate:

- `future/v4/evidence/v4_goal4617_catalog_gpu_after_grouped_i64_promotion_32768_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_catalog_gpu_after_grouped_i64_promotion_32768_2026-06-24.md`

Result:

- `status: passed`
- `mode: gpu`
- examples: 9
- grouped-i64 status: `measured`
- point-group status: `measured_candidate`
- frontdoor quickstart: `measured_surface_count: 4`, `candidate_surface_count: 1`

## Historical Evidence Note

Older evidence and review files still contain `candidate` wording for
grouped-i64 because they were generated before the `goal4617` promotion patch.
They are historical records and should not be rewritten. Current live code,
examples, docs, and new gate evidence use measured wording for grouped-i64.

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
2. Are R1/R2/R3/R4 from the original grouped-i64 review now closed?
3. Does the post-patch GPU catalog gate satisfy the measured-catalog gate?
4. Is the OptiX 8.0 maximum validated ABI scope visible enough in code/docs?
5. Is there any claim-status drift, release drift, true-zero-copy drift, or
   app-specific-kernel drift?
6. May `goal4617` be marked complete and may Codex begin `goal4618`?

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

