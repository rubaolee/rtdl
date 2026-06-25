# V4 Goal4638 Formal Release Scorecard Freeze

Status: `goal4638_formal_release_scorecard_frozen_pending_external_review_not_release`

Decision: `freeze_v4_release_scorecard_before_goal4639_pod_run`

## Correction Note

An AABB-after-catalog GPU regression gate was produced earlier under a Goal4638
filename. That gate is valid release-hardening evidence, but it is not the owner-approved Goal4638 exit gate. The owner-approved Goal4638 is the formal
release scorecard freeze. This document is the controlling Goal4638 artifact.

The catalog GPU gate remains input evidence:

- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json`
- `future/v4/v4_goal4638_catalog_regression_gpu_gate_after_aabb_2026-06-25.md`

## Purpose

Freeze the exact scorecard that Goal4639 must run on the POD. No benchmark
classification, threshold, inclusion rule, or public wording rule may change
after Goal4639 results are seen.

## Hardware And Software Scope

Goal4639 must run on the same RT hardware class used by the V4 gates:

- GPU class: NVIDIA RTX A5000 / Ampere
- validated driver family: 570.x
- validated OptiX ABI: 8.0
- Python: 3.12 compatible
- measured partners/scopes: `torch`, `numba`, `rtdl_native`

If a row cannot run because a dependency is missing, the row is recorded as
`blocked_by_environment` with exact dependency and command output. It is not
silently dropped.

## Benchmark Family Classification

The scorecard covers the 10 promoted benchmark families from the current V4
coverage audit.

| Family | Scorecard class | V4 operators/surfaces | Required Goal4639 action |
| --- | --- | --- | --- |
| `rt_dbscan` | `release_in_scope_strong_operator` | fixed-radius count-threshold; fixed-radius graph component-union | run mapped operator gates or explain hard blocker |
| `raydb_style` | `release_in_scope_strong_operator` | grouped-i64 reduction; closest-hit grouped argmin; any-hit flags | run mapped operator gates or explain hard blocker |
| `triangle_counting` | `release_in_scope_strong_operator` | any-hit weighted sum; grouped-i64 reduction | run mapped operator gates or explain hard blocker |
| `librts_spatial_index` | `release_in_scope_strong_operator` | AABB all-ops count | run mapped operator gate or explain hard blocker |
| `hausdorff_xhd` | `partial_operator_control` | nearest witness; fixed-radius count-threshold | run smoke/control only; cannot drive release geomean |
| `robot_collision` | `partial_operator_control` | any-hit flags | run smoke/control only; cannot drive release geomean |
| `contact_manifold` | `partial_operator_control` | nearest witness | run smoke/control only; cannot drive release geomean |
| `rtnn` | `partial_operator_control` | nearest witness | run smoke/control only; cannot drive release geomean |
| `spatial_rayjoin` | `deferred_excluded` | none in V4.0 | record exclusion and reason |
| `barnes_hut` | `deferred_excluded` | none in V4.0 | record exclusion and reason |

## Included Measured Surfaces

Goal4639 must include all 8 current measured surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`
6. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
7. `v4_fixed_radius_graph_component_union_3d_device_arrays`
8. `v4_aabb_index_query_2d_all_ops_count_prepared_runner`

Candidate surfaces: none.

## Baselines

Baselines are frozen per surface:

- fixed-radius count-threshold: Section 8 route-D / prepared-hot-path evidence;
- closest-hit grouped argmin: existing Torch CUDA device-array front-door gate;
- any-hit flags: existing Torch CUDA device-array front-door gate;
- grouped-i64 reduction: grouped width 1/16/256 RTX A5000 gates;
- point-group nearest witness: point-group POD gate and mixed6 diagonal gate;
- weighted sum: Goal4633 comparable-route gate;
- component union: Goal4635 Embree and legacy OptiX controls;
- AABB all-ops: Goal4636C Embree same-contract-family control.

Goal4639 may rerun the current examples/gates, but it must not change these
baseline classes after seeing results.

## Performance Floor Reference Table

Goal4639 pass/fail must use this table. The runner or reviewer must not choose
a weaker floor from upstream evidence after seeing the new results.

| Surface | Minimum floor | Observed anchor | Canonical source |
| --- | --- | --- | --- |
| `v4_fixed_radius_count_threshold_2d_device_arrays` | >=2 serious sizes with `device_array_to_route_d_rows_gap <=100.0` and `gap_reduction_over_prior_summary >=10.0`; correctness must pass at all frozen sizes | gap reduction `1022.93x`, `3841.66x`, `9699.17x`; device-array-to-Route-D-row gaps `0.442x`, `0.202x`, `0.118x` | `future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json` |
| `v4_closest_hit_grouped_argmin_3d_device_arrays` | device front door must beat legacy host-materialize route at all 3 frozen ray counts; ratio `>=1.0x`; correctness must pass | `1.542x`, `1.575x`, `1.729x`; summary median ratio `1.575x` | `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json` |
| `v4_ray_triangle_any_hit_flags_2d_device_arrays` | 8192-row Torch fixture reference ratio `>=1.0x`; all 3 frozen ray counts must pass correctness and keep `host_materialization_in_hot_path: false` | 8192-row Torch-reference ratio `9.379x`; 32768 and 131072 correctness pass with reference intentionally skipped by protocol | `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json` |
| `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | all 6 frozen rows must pass parity and same-contract ratio `>=1.0x` | `166.546x`, `411.867x`, `11.271x`, `21.369x`, `1.641x`, `2.978x`; observed min `1.641x` | `future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md` |
| `v4_point_group_nearest_witness_2d_device_arrays` | repeat-gate and mixed6 rows must pass parity and same-contract ratio `>=1.0x` at both serious sizes | repeat gate `663.143x`, `1868.088x`; mixed6 `509.391x`, `1863.097x`; observed min `509.391x` | `future/v4/point_group_device_array_frontdoor.md` |
| `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | each frozen shape ratio `>=1.20x` and four-shape geomean `>=1.50x`; parity must pass at every shape | `2.1459x`, `1.6329x`, `1.3564x`, `1.2011x`; geomean `1.5457x` | `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json` |
| `v4_fixed_radius_graph_component_union_3d_device_arrays` | `runner_vs_embree_hot >=1.20x`, `runner_vs_embree_wall >=1.20x`, `runner_vs_legacy_wall >=0.98x`, and component signatures must match | runner vs Embree hot `1.393x`; runner vs Embree wall `1.600x`; runner vs legacy wall `1.208x`; all canonical signatures match | `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json` |
| `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | cross-backend count parity must pass; accepted contract family must pass; Embree/OptiX query median `>=10.0x` and query total `>=10.0x` | query median `264.822x`; query total `115.007x`; cross-backend count parity true | `future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json` |

## Thresholds

For `release_in_scope_strong_operator` rows:

- correctness/parity must pass;
- all claim-boundary flags must stay false;
- every mapped measured surface must either:
  - pass its already frozen surface-specific performance floor, or
  - be recorded as `blocked_or_failed` with exact failed check;
- no strong row may be silently skipped.

For `partial_operator_control` rows:

- correctness/smoke must pass if runnable;
- performance may be reported, but it cannot contribute to release geomean or
  broad speedup wording.

For `deferred_excluded` rows:

- no runtime performance is required;
- the exclusion reason must be included in the Goal4639 output.

## Score Aggregation

Goal4639 must compute:

- strong-row pass count and fail count;
- measured-surface pass count and fail count;
- partial-control pass/fail/blocked count;
- deferred-excluded count;
- per-surface ratios where applicable;
- a release decision recommendation:
  - `release_candidate_possible_pending_3ai` only if all strong rows and all
    measured surfaces pass and docs/review debt are clean enough for final
    review;
  - `performance_preview_only` if any strong row or measured surface fails;
  - `blocked_incomplete` if environment failures prevent a fair reading.

No geomean can include partial or deferred rows. No broad whole-app speedup
wording is authorized by this scorecard.

## Allowed Public Wording After Goal4639

Allowed if the scorecard passes:

- "V4 has measured high-performance generic RT-core operator surfaces for the
  documented measured scopes."
- "Measured surfaces are bounded by partner/hardware/surface-specific evidence."

Forbidden regardless of Goal4639 result unless a later final 3-AI release
authorization explicitly changes it:

- "all benchmark apps are faster"
- "whole-application speedup"
- "broad V4 speedup"
- "public true zero copy"
- "CuPy performance"
- "Tier-3 callbacks are supported"
- "C ABI / embedding / non-Python host support"
- "LibRTS paper reproduced"
- "Barnes-Hut / Spatial RayJoin covered by V4.0"

## Goal-Level Decision Audit

1. Was the previous Goal4638 catalog-gate naming stupid?
   Yes. It produced valid evidence but used the wrong goal label compared with
   the owner-approved plan.

2. What action made it stupid?
   I followed the immediate release-hardening instinct and did not re-read the
   approved Goal4638/4639 definitions before naming the result.

3. Was there a better path?
   Yes. Treat catalog regression as input evidence, then freeze the formal
   scorecard before any all-app/promoted benchmark POD run.

4. Can the path change now to solve the real problem?
   Yes. This document is the controlling correction: Goal4639 is blocked until this scorecard freeze receives external review.

## Review Requirement

Claude + Antigravity review is required before Goal4639. If one reviewer returns
empty output, record review debt; do not run Goal4639 as a release scorecard
until at least one substantive external review approves the frozen scorecard
and the missing seat is explicitly tracked.

## Non-Authorization

This scorecard freeze does not authorize V4 release, release-candidate wording,
broad V4 speedup claims, whole-app speedup claims, all-benchmark speedup claims,
public true-zero-copy claims, Tier-3 callback support, raw OptiX callback
support, CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
