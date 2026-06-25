# Call For Review: `goal4617` Grouped-I64 Promotion Decision

Date: 2026-06-24
Author: Codex
Status: promotion-decision request, not a catalog change

## Scope

This packet asks whether the V4 grouped-i64 candidate should be authorized for
a measured-catalog promotion patch.

Candidate surface:

- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

Generic primitive:

- `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`

This is a generic Tier-2 fused operator candidate. It is not an app-specific
kernel and must not be described as Barnes-Hut, RayDB, DBSCAN, or any other app
identity.

## Decision Requested

Choose one:

1. `authorize_grouped_i64_promotion_patch`
   - Codex may apply the atomic promotion patch:
     - move grouped-i64 from candidate catalog to measured catalog
     - mark Torch as measured for this surface
     - leave CuPy declared-unmeasured
     - update front-door measured count from 3 to 4
     - update GPU catalog gate to include grouped-i64 as measured
     - run local tests and POD GPU catalog gate
   - Final `goal4617` closure still requires post-patch 3-AI completion review.

2. `keep_grouped_i64_candidate`
   - Do not promote.
   - Record why the evidence is insufficient.
   - Continue to `goal4618` or another agreed target without changing catalog
     classification.

No option authorizes V4 release or broad speedup wording.

## Prior Review Baseline

Claude grouped-i64 candidate review:

- `future/v4/reviews/claude_v4_primitive_grouped_i64_candidate_review_2026-06-24.raw.md`

Prior verdict:

- `accept_with_required_amendments_before_catalog_decision`

Prior required amendments:

1. R1: candidate must be included in the GPU-mode catalog regression gate before
   a valid measured-catalog promotion.
2. R2: measured-partner status must be updated atomically in catalog and claim
   boundary only when promotion is authorized.
3. R3: OptiX ABI status must be formally scoped.
4. R4: quickstart/catalog measured count must update from 3 to 4 only when
   promotion is authorized.

This packet does not claim R1/R2/R4 are already applied in code. It asks for
authorization to apply the atomic promotion patch and then validate it. R3 is
addressed below as the proposed scope statement.

## New Evidence Added For `goal4617`

Claude's advisory A1 requested multiple group widths or an explicit validated
scope. Codex ran a multi-width RTX A5000 POD gate with:

- ray counts: `32768`, `131072`
- repeats: `7`
- warmups: `2`
- group widths: `1`, `16`, `256`
- hardware: NVIDIA RTX A5000
- driver: `570.195.03`
- Python: `3.12.3`
- Torch: `2.8.0+cu128`

Evidence files:

- `future/v4/evidence/v4_goal4617_grouped_i64_width1_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width16_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width256_pod_gate_32768_131072_2026-06-24.json`

All runs passed parity for:

- `sum_count`
- `min`
- `max`

Every run compares the direct device-output front door against the legacy
prepared native host-output route for the same prepared scene, ray batch, and
primitive payload.

## New POD Results Summary

| group_width | ray_count | group_count | parity | legacy-host / device-output median ratio | device median s | legacy median s |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 32,768 | 32,768 | pass | 166.545732x | 0.000183366 | 0.030538864 |
| 1 | 131,072 | 131,072 | pass | 411.866531x | 0.000377137 | 0.155330196 |
| 16 | 32,768 | 2,048 | pass | 11.270692x | 0.000147447 | 0.001661830 |
| 16 | 131,072 | 8,192 | pass | 21.369330x | 0.000222642 | 0.004757710 |
| 256 | 32,768 | 128 | pass | 1.641351x | 0.000145189 | 0.000238307 |
| 256 | 131,072 | 512 | pass | 2.977954x | 0.000419069 | 0.001247969 |

Interpretation:

- The benefit is largest when the legacy route must materialize many grouped
  host rows.
- The low-row-count end (`group_width=256`) still passes parity and remains
  above parity in the measured runs.
- This is an operator-level same-contract comparison only. It does not
  authorize broad V4 or whole-app speedup claims.

## Claim Boundary Observations

Evidence metadata records:

- `host_materialization_in_hot_path: false`
- `group_rows_downloaded_to_host_in_hot_path: false`
- `native_direct_device_output_columns: true`
- `prepared_primitive_payload_used: true`
- `prepared_ray_batch_used: true`
- `primitive_payload_prepare_is_hot_path: false`
- `python_ray_object_boundary_in_hot_path: false`
- `true_zero_copy_authorized: false`
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`

The claim boundary is appropriate for a measured Tier-2 operator only if
promotion is authorized. It is not a true-zero-copy claim.

## Proposed OptiX ABI Scope Statement

The validated promotion scope is:

- OptiX ABI: `8.0`
- GPU: NVIDIA RTX A5000 / Ampere
- driver observed: `570.195.03`
- Python: `3.12.3`
- partner: Torch CUDA (`torch 2.8.0+cu128`)

OptiX 9.1 is not validated for this surface. Earlier POD setup observed OptiX
9.1 rejection on driver `570.195.03`; therefore any measured-catalog promotion
must explicitly state that OptiX 8.0 is the maximum validated ABI for this
surface until a separate OptiX 9.1 machine accepts and passes the gate.

## Proposed Atomic Promotion Patch If Authorized

If reviewers choose `authorize_grouped_i64_promotion_patch`, Codex should apply
one atomic patch that:

1. Moves `primitive_grouped_i64_reduction` from
   `V4_TIER2_CANDIDATE_OPERATOR_SURFACES` to `V4_TIER2_OPERATOR_SURFACES` in
   `src/rtdsl/v4_operator_catalog.py`.
2. Sets `measured_partners=("torch",)` for this surface and keeps
   `declared_unmeasured_partners=("cupy",)`.
3. Updates
   `primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4()` in
   `src/rtdsl/v4_ray_triangle.py` so Torch reports measured and CuPy reports
   declared-unmeasured.
4. Updates `src/rtdsl/v4.py` so grouped-i64 is a measured surface and only the
   point-group nearest-witness surface remains candidate.
5. Updates `future/v4/examples/primitive_grouped_i64_reduction_torch_device_arrays.py`
   so its GPU status is `measured`, not `measured_candidate`, and removes the
   candidate-status field from measured output.
6. Updates `scripts/v4_catalog_regression_gate.py` so grouped-i64 is part of
   the GPU-mode measured catalog gate and the front-door quickstart expects
   `measured_surface_count == 4`.
7. Updates tests and docs to match the measured/candidate split.
8. Runs local tests and the GPU catalog gate on the POD.

The patch must preserve:

- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`
- `true_zero_copy_authorized: false`
- CuPy performance claims remain unauthorized

## Recommendation

Codex recommendation:

- `authorize_grouped_i64_promotion_patch`

Reason:

- The candidate is generic and app-name-free.
- The device-output route has parity across multiple reductions.
- The new multi-width POD evidence closes the narrow group-width concern.
- The low-row-count case still remains above parity while the high-row-count
  cases show large operator-level same-contract gains.
- The claim boundary is conservative and does not authorize release or broad
  speedup wording.

This recommendation is not self-authorization. The catalog must not be changed
until external reviewers accept this decision.

## Questions For Reviewers

1. Should grouped-i64 be authorized for the atomic measured-catalog promotion
   patch, or kept as candidate?
2. Does the new group-width evidence close the prior A1 coverage concern?
3. Is the OptiX 8.0 maximum-validated ABI scope acceptable for measured-catalog
   promotion, or must OptiX 9.1 be tested first?
4. Are the proposed patch steps sufficient to satisfy R1/R2/R4 without claim
   drift?
5. Are any additional correctness or performance gates required before the
   patch may be applied?
6. If promotion is authorized and the post-patch GPU gate passes, may `goal4617`
   proceed to 3-AI completion review?

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

