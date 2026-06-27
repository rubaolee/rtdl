# Call For Review: `goal4618` Point-Group Promotion Decision

Date: 2026-06-24
Author: Codex
Status: promotion-decision request, not a catalog change

## Scope

This packet asks whether the V4 point-group nearest-witness candidate should be
authorized for a measured-catalog promotion patch.

Candidate surface:

- `v4_point_group_nearest_witness_2d_device_arrays`

Generic primitive:

- `POINT_GROUP_NEAREST_WITNESS_2D`

This is a generic Tier-2 fused operator candidate. It is not an app-specific
kernel and must not be described as a spatial-join, DBSCAN, Barnes-Hut, or
domain-specific route.

## Important Boundary

This surface is narrower than full input zero-copy:

- RTDL owns and prepares the search points and point groups into a native scene.
- The hot run accepts Torch CUDA query columns directly.
- The hot run writes Torch CUDA output columns directly.
- The hot run does not upload host query rows and does not download neighbor
  rows.

Allowed wording:

- direct device query columns
- direct device output columns
- caller-owned Torch CUDA query/output columns

Forbidden wording:

- true zero-copy
- all inputs caller-owned GPU arrays
- whole-application speedup
- broad V4 speedup

## Decision Requested

Choose one:

1. `authorize_point_group_promotion_patch`
   - Codex may apply the atomic promotion patch:
     - move point-group nearest-witness from candidate catalog to measured
       catalog
     - mark Torch as measured for this surface
     - leave CuPy declared-unmeasured
     - update front-door measured count from 4 to 5
     - update candidate count from 1 to 0
     - update GPU catalog gate to include point-group as measured
     - run local tests and POD GPU catalog gate
   - Final `goal4618` closure still requires post-patch 3-AI completion review.

2. `keep_point_group_candidate`
   - Do not promote.
   - Record what evidence is missing.
   - Continue to `goal4619` or another agreed target without changing catalog
     classification.

No option authorizes V4 release or broad speedup wording.

## Prior Review Baseline

Claude amendment-closure review:

- `future/v4/reviews/claude_v4_point_group_candidate_amendment_closure_review_2026-06-24.raw.md`

Prior verdict:

- `accept_amendments_closed_continue_to_promotion_decision`

Closed amendments:

1. A1: candidate-path sub-field naming uses direct device read/write wording,
   not misleading `*_true_zero_copy_authorized` sub-fields.
2. A2: Torch and CuPy partner statuses are separated.
3. A3: non-trivial fixture includes exact, nonzero-distance, no-hit, and
   opposite-offset rows.

Prior non-authorization:

- Amendment closure did not authorize promotion.

## Original POD Evidence

Original point-group POD evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`

Original fixture:

- exact match
- x-positive nonzero hit
- y-axis no-hit
- x-negative nonzero hit

Original result:

| query_count | parity | legacy-host / device-output median ratio |
| ---: | --- | ---: |
| 32,768 | pass | 663.142819x |
| 131,072 | pass | 1868.087890x |

## New Goal4618 Evidence

Claude's prior review noted that a full pre-release review should include a
non-axis no-hit. Codex added a `mixed6` fixture variant to:

- `scripts/v4_point_group_nearest_witness_device_outputs_validation.py`

The `mixed6` fixture includes:

- exact match
- x-positive nonzero hit
- y-axis no-hit
- x-negative nonzero hit
- diagonal hit
- diagonal no-hit

POD evidence:

- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.md`

Result:

| query_count | fixture | parity | legacy-host / device-output median ratio | direct median s | legacy median s |
| ---: | --- | --- | ---: | ---: | ---: |
| 32,768 | mixed6 | pass | 509.390582x | 0.000575196 | 0.292999424 |
| 131,072 | mixed6 | pass | 1863.096663x | 0.000475917 | 0.886679396 |

The first `mixed6` attempt failed because the test oracle used float64 distance
math while the native path reports float32-distance semantics. Device output and
legacy rows agreed on neighbor IDs and sample distances. Codex corrected the
oracle to the native float32 coordinate model and reran the same gate
successfully. The failed attempt is not used as promotion evidence.

## Claim Boundary Observations

Evidence metadata records:

- `host_materialization_in_hot_path: false`
- `host_query_upload_in_hot_path: false`
- `neighbor_rows_downloaded_to_host_in_hot_path: false`
- `query_point_columns_direct_device_read_confirmed: true`
- `output_columns_direct_device_write_confirmed: true`
- `native_direct_device_output_columns: true`
- `true_zero_copy_authorized: false`
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`

This claim boundary is appropriate for a measured Tier-2 operator only if
promotion is authorized. It is not a true-zero-copy claim.

## Proposed Scope Statement If Authorized

The validated promotion scope should be:

- prepared search/groups: RTDL-owned native scene
- hot inputs: Torch CUDA query columns
- hot outputs: Torch CUDA witness columns
- OptiX ABI: 8.0 maximum validated
- GPU: NVIDIA RTX A5000 / Ampere
- driver observed: 570.195.03
- partner: Torch CUDA (`torch 2.8.0+cu128`)

CuPy and OptiX 9.1 remain unmeasured.

## Proposed Atomic Promotion Patch If Authorized

If reviewers choose `authorize_point_group_promotion_patch`, Codex should apply
one atomic patch that:

1. Moves `point_group_nearest_witness` from
   `V4_TIER2_CANDIDATE_OPERATOR_SURFACES` to `V4_TIER2_OPERATOR_SURFACES` in
   `src/rtdsl/v4_operator_catalog.py`.
2. Sets `measured_partners=("torch",)` and keeps
   `declared_unmeasured_partners=("cupy",)`.
3. Updates
   `point_group_nearest_witness_2d_device_array_claim_boundary_v4()` in
   `src/rtdsl/v4_point_group.py` so Torch reports measured and CuPy reports
   declared-unmeasured.
4. Updates `src/rtdsl/v4.py` so point-group is a measured surface and there are
   no current candidate surfaces.
5. Updates `future/v4/examples/point_group_nearest_witness_torch_device_arrays.py`
   so its GPU status is `measured`, not `measured_candidate`.
6. Updates `scripts/v4_catalog_regression_gate.py` so point-group is part of
   the GPU-mode measured catalog gate and the front-door quickstart expects
   `measured_surface_count == 5`, `candidate_surface_count == 0`.
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

- `authorize_point_group_promotion_patch`

Reason:

- Amendment closure is already accepted by Claude.
- The original serious POD evidence is strong.
- The new `mixed6` gate adds diagonal hit/no-hit coverage and passes parity.
- The claim boundary is conservative and clearly excludes true-zero-copy and
  release-speedup wording.
- The operator remains generic and app-name-free.

This recommendation is not self-authorization. The catalog must not be changed
until external reviewers accept this decision.

## Questions For Reviewers

1. Should point-group nearest-witness be authorized for the atomic
   measured-catalog promotion patch, or kept as candidate?
2. Does the new `mixed6` POD evidence close the non-axis no-hit coverage concern?
3. Is the narrower prepared-search/groups boundary acceptable for a measured
   surface if the hot query/output path is direct device-array?
4. Is the OptiX 8.0 maximum-validated ABI scope acceptable, or must OptiX 9.1 be
   tested first?
5. Are the proposed patch steps sufficient without claim drift?
6. Are any additional correctness or performance gates required before the
   patch may be applied?
7. If promotion is authorized and the post-patch GPU gate passes, may
   `goal4618` proceed to 3-AI completion review?

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

