# V4 Goal4647: V2.14 Partner Inventory With V4 Boundary Ledger

Date: 2026-06-25
Status: candidate completion record, pending external completion review
Goal chain:
`future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md`
Machine-readable evidence:
`future/v4/evidence/v4_goal4647_partner_inventory_2026-06-25.json`

## Purpose

Goal4647 answers one narrow question before any new V4 partner promotion work:

```text
Which CuPy / Numba assets already existed in V2.14 or Phoenix V3, and which of
them may become V4-certified generic partner surfaces without pretending that
partner migration is a new V4 speed win?
```

This is a boundary ledger, not a release claim. It records historical partner
strength honestly and prevents the common mistake Claude flagged in AM1:
moving an old V2.14 CuPy or Numba win behind a V4 front door does not by itself
prove V4 is faster than V2.14.

## Current V4 Truth Ledger

| Topic | Current truth | Claim status |
|---|---|---|
| V4 release shape | V4.0.0 is currently a bounded operator release with eight measured generic Tier-2 surfaces. | Operator-level only, not whole-app. |
| Torch partner | Torch CUDA is the main measured V4 device-array partner. | Measured for current catalog surfaces. |
| CuPy partner | CuPy has strong V2/V3 historical evidence, but no V4-certified CuPy performance surface yet. | Blocked until Goal4649. |
| Numba partner | Fixed Numba continuation evidence exists; arbitrary callback support remains Tier-3 spike-only. | Fixed-continuation only after certification. |
| Broad speedup | No complete app-level V4 vs V2.14/V3 benchmark has passed. | Blocked until Goals4653-4655. |

## Integrity Locks

- Partner migration is not a V4 speed win.
- Partner parity is not a V4 speed win.
- Historical V2.14/V3 ratios may select candidates for rerun, but cannot become
  public V4 performance claims without a V4 run.
- CuPy performance wording remains blocked until Goal4649 certifies exact V4
  surfaces.
- Numba support wording remains limited to fixed certified continuations;
  arbitrary callbacks remain unsupported.
- Barnes-Hut partner routes remain no-go evidence for V4.0 Tier-2 promotion,
  because the useful wins are not clean RT-core generic-operator wins.

## Inventory Summary

The machine-readable inventory contains 12 rows:

| Classification | Count | Meaning |
|---|---:|---|
| `promotion_candidate_strong` | 2 | Strong historical partner evidence, suitable for first V4 certification attempts. |
| `promotion_candidate_needs_rerun` | 5 | Plausible generic partner surfaces, but V4 contract, denominator, and scale must be rerun. |
| `historical_only` | 3 | Useful context or already-covered current V4 surface; not a new V4 promotion target. |
| `rejected_or_no_go` | 2 | Do not promote for V4.0 Tier-2 release wording. |

## Candidate Rows

| ID | Partner | Family / app | Classification | Historical result | V4 action |
|---|---|---|---|---|---|
| `cupy_grouped_reduction_device_columns_262144` | CuPy | RayDB-style grouped reduction | `promotion_candidate_strong` | 262144 rows / 1024 groups: 3.599x over host-packed OptiX; 100.019x over same-contract Embree context. | Goal4649 CuPy front-door certification target. |
| `cupy_grouped_reduction_device_columns_524288` | CuPy | RayDB-style grouped reduction | `promotion_candidate_strong` | 524288 rows / 2048 groups: 73.586x over host-packed OptiX; 174.645x over same-contract Embree context. | Goal4649 CuPy front-door certification target. |
| `hit_stream_payload_grouped_sum_f64_cupy_consumer` | CuPy | RayDB-style / triangle fallback | `promotion_candidate_needs_rerun` | Historical fallback/comparison route; V4 denominator not frozen. | Rerun only as partner fallback/baseline; not a V4 speed proof. |
| `cupy_hausdorff_witness_continuation` | CuPy | Hausdorff witness | `promotion_candidate_needs_rerun` | Goal2048: loses small, parity around 1024x1024, wins at 2048x2048. | Goal4649 candidate if mapped to nearest-witness/generic witness continuation. |
| `cupy_segment_polygon_hitcount_prepared_scaling` | CuPy | Robot collision / hitcount | `promotion_candidate_needs_rerun` | Goal2054: strict-parity prepared rows from 8192 to 65536. | Goal4649 candidate if mapped to any-hit flags/hitcount. |
| `v2_cupy_control_apps_rawkernel_large_scale` | CuPy | V2.0 control-app matrix | `historical_only` | Strong large-scale CuPy evidence across old control rows. | Background only; promote generic operators, not old app identities. |
| `rtdbscan_prepared_optix_cupy_grouped_stream_component_labels_3d` | CuPy | RTDBSCAN | `promotion_candidate_needs_rerun` | V2.14 all-app evidence records CuPy grouped-stream component-label route. | Goal4649 if CuPy component labels retained; otherwise Goal4650 fixed Numba route. |
| `numba_component_union_current_v4_surface` | Numba | RTDBSCAN / component union | `historical_only` | Current V4 already measures fixed-radius graph component union at representative 1.203x. | Already bounded V4 operator surface; no broad app claim. |
| `barnes_hut_aggregate_tree_numba_cuda_fused` | Numba CUDA | Barnes-Hut | `rejected_or_no_go` | 131072 bodies: 45.493 ms, 4.082x over CPU/Numba fused; no RT-core V4 claim. | Do not promote as V4.0 generic Tier-2. |
| `barnes_hut_optix_cupy_or_optix_numba_frontier` | CuPy / Numba | Barnes-Hut frontier | `rejected_or_no_go` | Same-basis no-go: OptiX+partner frontier routes slower than fastest Numba CUDA fused route. | Keep as negative evidence. |
| `rtnn_prepared_ranked_summary_cupy_reference` | CuPy | RTNN | `promotion_candidate_needs_rerun` | 7.889x hot query, 1.315x cold+query, 3.761x runner-wall over CuPy uniform-grid reference. | Later route-binding candidate; no whole-app claim. |
| `tier3_numba_ptx_spike` | Numba | Custom callback | `historical_only` | PTX generation passed narrowly; OptiX module link failed. | Tier-3 spike-only; arbitrary callback unsupported. |

## Goal4649 CuPy Targets

The strongest immediate CuPy certification targets are:

- `cupy_grouped_reduction_device_columns_262144`
- `cupy_grouped_reduction_device_columns_524288`
- `cupy_segment_polygon_hitcount_prepared_scaling`
- `cupy_hausdorff_witness_continuation`

These are targets for V4 rerun and certification, not public claims. Goal4649
must use the Goal4648 contract, include correctness parity, record denominator
and scale, and fail closed if the V4 front door cannot reproduce the route.

## Goal4650 Numba Target

The only immediate Numba continuation target is:

- `numba_component_union_current_v4_surface`

This row is already a bounded V4 measured operator surface. Goal4650 should not
reinterpret it as a new speed claim; it should use the row to confirm the fixed
Numba continuation contract and decide whether any additional fixed-continuation
variants need certification, while potential future CuPy variant promotion is tracked
separately. This does not authorize arbitrary user callback support. It remains fixed
continuation support only.

## What This Does Not Authorize

This Goal4647 record does not authorize:

- V4 release/tag language;
- broad V4 speedup language;
- app-level V4-vs-V2.14 claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- treating partner migration as V4 speed evidence;
- using Barnes-Hut partner routes as V4.0 generic Tier-2 evidence.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

No for this step. The work stayed on the revised Claude-approved route:
inventory first, boundary lock first, no benchmark or claim expansion.

2. If yes, what actions made it foolish?

Not applicable. The main risk was turning old V2.14 partner wins into fake V4
speed claims; this ledger explicitly blocks that path.

3. Was there another path that avoided being trapped in one idea?

Yes: we could have skipped inventory and jumped straight to CuPy benchmarking.
That would have been faster but unsafe, because it would not distinguish
partner migration from true V4 operator improvement.

4. Can we try a different path that solves the real problem?

The real path is Goal4648 then Goal4649/4650: define numeric partner contracts,
rerun exact V4 surfaces, and classify results by claim type.

## Exit Status

Goal4647 has enough local evidence for completion review:

- JSON inventory parses successfully.
- The ledger records current V4 truth.
- The ledger preserves the AM1 partner-migration lock.
- The ledger identifies concrete Goal4649/4650 targets.
- No performance claim or release wording is authorized.

External completion review is still required, or recorded review debt if a
reviewer is unavailable under the user's rule.
