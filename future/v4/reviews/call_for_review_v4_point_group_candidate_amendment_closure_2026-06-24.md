# Call For Review: V4 Point-Group Candidate Amendment Closure

Date: 2026-06-24
Requested verdict label: one of

- `accept_amendments_closed_continue_to_promotion_decision`
- `accept_with_remaining_required_amendments`
- `reject_candidate_boundary_or_correctness_problem`
- `blocked_insufficient_evidence`

## Context

Claude's first review of the point-group nearest-witness V4 candidate returned
`accept_with_required_amendments_before_catalog_decision`.

Candidate surface:

- `v4_point_group_nearest_witness_2d_device_arrays`

This packet asks only whether the required amendments are closed. It does not
request release authorization or measured-catalog promotion.

## Files To Review

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v4_point_group.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4_operator_catalog.py`
- `scripts/v4_point_group_nearest_witness_device_outputs_validation.py`
- `future/v4/point_group_device_array_frontdoor.md`
- `future/v4/reviews/point_group_nearest_witness_candidate_amendment_closure_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_point_group_nearest_witness_candidate_2026-06-24.md`

Evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.md`

## Claimed Amendment Closure

### A1: misleading true-zero-copy sub-fields

Claimed closed for the point-group candidate path. Candidate metadata no longer
emits:

- `query_point_columns_true_zero_copy_authorized`
- `output_columns_true_zero_copy_authorized`

It now emits:

- `query_point_columns_direct_device_read_confirmed`
- `output_columns_direct_device_write_confirmed`

The authoritative boundary remains:

- `true_zero_copy_authorized: false`

### A2: partner classification

Claimed closed. Candidate metadata now separates:

- `pod_candidate_partners: ["torch"]`
- `partner_support_declared_unmeasured: ["cupy"]`

The same boundary fix was applied to the grouped-i64 candidate.

### A3: non-trivial correctness fixture

Claimed closed. The POD repeat gate no longer uses an all-exact fixture. It now
uses equal counts of:

- exact matches
- positive-offset nonzero nearest distances
- no-hit rows
- negative-offset nonzero nearest distances

No-hit rows are checked against neighbor id `0xFFFFFFFF` and float32 max
distance.

RTX A5000 POD repeat gate:

| queries | parity | direct device-output median | legacy host-row median | ratio |
|---:|---|---:|---:|---:|
| 32,768 | pass | 0.000529401s | 0.351068474s | 663.143x |
| 131,072 | pass | 0.000506975s | 0.947073404s | 1868.088x |

The include-candidates GPU catalog gate also passed with nine examples:
three measured V4 surfaces, two candidate surfaces, the front-door quickstart,
and three callback planner cases.

## Questions For Reviewer

1. Are A1, A2, and A3 actually closed for the point-group candidate?
2. Is any remaining `*_true_zero_copy_authorized` metadata outside this
   candidate path a blocker for this closure decision, or should it be handled
   as separate measured-surface wording debt?
3. Does the non-trivial fixture sufficiently exercise no-hit and nonzero
   distance correctness for this candidate's current promotion-review scope?
4. Is the same-contract ratio wording still honest: old host-row
   materialization route versus direct device-query/device-output route?
5. If accepted, is the only next decision a separate measured-catalog
   promotion decision requiring external consensus?

## Non-Authorization

This packet does not authorize V4 release, measured catalog promotion, broad V4
speedup wording, whole-application speedup wording, true-zero-copy public
wording, CuPy performance claims, Tier-3 callback/PTX support, embedding/C-ABI,
non-Python host bindings, or app-specific native kernels.
