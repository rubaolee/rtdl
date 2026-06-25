# V4 `goal4616` Status Ledger

Date: 2026-06-24
Status: complete with 3-AI completion consensus

## Purpose

This ledger records the current V4 surface truth before further implementation.
It is an audit artifact only. It does not change measured/candidate
classification and does not authorize release wording.

## Goal Context

The forward goals are defined in:

- `future/v4/reviews/call_for_review_v4_goal4615_goal4623_forward_goals_2026-06-24.md`

Claude amendment closure authorized beginning `goal4616` in:

- `future/v4/reviews/claude_v4_goal4615_goal4623_forward_goals_amendment_check_2026-06-24.raw.md`

`goal4615` third-seat review remains debt and is recorded in:

- `future/v4/reviews/goal4615_review_debt_and_authorization_record_2026-06-24.md`

## Current V4 Surface Truth

### Measured Surfaces

The current measured V4 catalog contains exactly three Torch surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`

The front-door quickstart and catalog gate still report:

- `measured_surface_count: 3`
- `candidate_surface_count: 2`
- `candidate_operator_count: 2`

This ledger does not promote any candidate and does not change that count.

### Candidate Surfaces

The current candidate surfaces are:

1. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
2. `v4_point_group_nearest_witness_2d_device_arrays`

Both candidates have POD evidence, but neither is a measured catalog surface.
Both require separate promotion-decision review before any catalog change.

## Candidate Review Status

### Grouped-I64 Candidate

Surface:

- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

Primary evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`

Claude review:

- `future/v4/reviews/claude_v4_primitive_grouped_i64_candidate_review_2026-06-24.raw.md`

Claude verdict:

- `accept_with_required_amendments_before_catalog_decision`

Required before any measured-catalog decision:

1. R1: include the surface in the GPU-mode catalog gate if promotion is proposed.
2. R2: atomically move measured-partner status only if promotion is authorized.
3. R3: formally state OptiX ABI scope, especially OptiX 8.0 vs 9.1.
4. R4: update measured-surface count from 3 to 4 only if promotion is authorized.

Current classification:

- Candidate only.
- Torch is a POD candidate partner, not a measured catalog partner.
- CuPy remains declared-unmeasured.

### Point-Group Candidate

Surface:

- `v4_point_group_nearest_witness_2d_device_arrays`

Primary evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`

Claude amendment closure:

- `future/v4/reviews/claude_v4_point_group_candidate_amendment_closure_review_2026-06-24.raw.md`

Claude verdict:

- `accept_amendments_closed_continue_to_promotion_decision`

Closed amendments:

1. A1: candidate-path sub-field naming uses direct device read/write wording,
   not misleading `*_true_zero_copy_authorized` sub-fields.
2. A2: Torch and CuPy partner statuses are separated.
3. A3: non-trivial fixture includes exact, nonzero-distance, no-hit, and
   opposite-offset rows.

Current classification:

- Candidate only.
- Amendment closure does not authorize promotion.
- Torch is a POD candidate partner, not a measured catalog partner.
- CuPy remains declared-unmeasured.

## Known Wording Debt

Known wording debt remains outside the point-group candidate path:

- Some grouped-union and fixed-radius paths still contain older
  `*_true_zero_copy_authorized` sub-field wording.
- These are not blockers for the point-group candidate closure, but they must
  be audited before any affected surface promotion or release wording.

Safe wording for current V4 surfaces:

- "direct device-array handoff"
- "direct device read/write confirmed"
- "caller-owned device output columns"

Unsafe without separate authorization:

- "true zero-copy"
- "whole-app speedup"
- "broad V4 speedup"
- "raw OptiX callback support"

## 3D Fixed-Radius Risk Carried Into `goal4619`

The attractive 3D fixed-radius count-threshold expansion is not yet an honest
V4 device-array surface.

Current risk:

- The existing 3D route appears to be RTDL-owned prepared search with host query
  points and device output columns, not full caller-supplied GPU-array query
  columns.

Required next gate:

- `goal4619` must determine whether real 3D device-column search/query/output
  routing exists or can be bounded. If not, the 3D path must be reframed or
  deferred instead of being wrapped misleadingly.

## Local Validation

Unit tests passed:

```text
py -3 -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_scope_gate_test tests.v4_release_candidate_packet_test tests.v4_catalog_regression_gate_test tests.v4_point_group_nearest_witness_device_outputs_validation_test
```

Result:

```text
Ran 35 tests in 9.308s
OK
```

Dry-run catalog gate passed:

```text
py -3 scripts/v4_catalog_regression_gate.py --mode dry-run --include-candidates --json-out future/v4/evidence/v4_goal4616_catalog_dry_run_include_candidates_2026-06-24.json --md-out future/v4/evidence/v4_goal4616_catalog_dry_run_include_candidates_2026-06-24.md
```

Evidence:

- `future/v4/evidence/v4_goal4616_catalog_dry_run_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4616_catalog_dry_run_include_candidates_2026-06-24.md`

Gate result:

- `status: passed`
- `mode: dry-run`
- `include_candidates: true`
- `measured_surface_count: 3`
- `candidate_surface_count: 2`
- `release_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`
- `app_specific_native_kernel_authorized: false`

## Claim-Status Integrity Check

This ledger introduces no claim-status changes.

It does not:

- promote grouped-i64
- promote point-group
- increase measured surface count
- authorize V4 release
- authorize broad speedup wording
- authorize true-zero-copy wording
- authorize Tier-3 callback support
- authorize app-specific native kernels

## Completion Review

`goal4616` completion requires 3-AI consensus.

Current status:

- Codex implementation/audit seat: present
- Claude completion review: present
- Antigravity completion review: present

Completion review evidence:

- `future/v4/reviews/claude_v4_goal4616_status_ledger_completion_review_2026-06-24.raw.md`
- `future/v4/reviews/antigravity_v4_goal4616_status_ledger_completion_review_2026-06-24.raw.md`

Claude verdict:

- `accept_goal4616_implementation_complete_pending_3ai_debt`

Antigravity verdict:

- `accept_goal4616_complete`

With Codex + Claude + Antigravity, `goal4616` is fully closed. Both external
reviews authorize beginning `goal4617` and preserve all non-authorization
boundaries.
