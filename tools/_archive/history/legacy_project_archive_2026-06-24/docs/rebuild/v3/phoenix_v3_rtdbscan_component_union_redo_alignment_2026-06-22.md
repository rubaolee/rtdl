# Phoenix V3 RTDBSCAN Component-Union Redo Alignment

Date: 2026-06-22
Status: `rtdbscan_component_union_redo_aligned_reusable_capability_not_release`

This closes the Phoenix redo interpretation for the RTDBSCAN component-signature
work. The retained capability is `component_union`, not "RTDBSCAN is solved":

```text
generic_capability: component_union
app_probe: rt_dbscan
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
app_specific_native_engine_logic_allowed: false
```

## Retained Row

Exactly one RTDBSCAN-linked row remains in the current internal
13-row / 9-capability Phoenix surface:

```text
row_id: component_union_clustered3d_65536_524288_repeat5_row_scoped
packet: docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.json
status: row-scoped M7 after Claude repeat=5 Option B review and Codex consensus
```

The approved row is a same-contract component-signature route:

```text
Embree mode: embree_core_flags_numba_prepared_grid_column_signature_3d
OptiX mode: optix_rt_core_flags_numba_prepared_grid_column_signature_3d
Continuation: numba_label_count_and_flag_count_label_columns
point_ids materialized for signature: false
core_flags materialized for signature: false
native DBSCAN ABI added: false
```

The approved wording is limited to zero-noise four-cluster synthetic
`clustered3d` rows from 65,536 to 524,288 points, repeat=5. The end-to-end
OptiX-over-Embree range is 1.102x to 1.236x under that exact contract.

## Why This Stays In V3

The row captures a reusable `component_union` continuation capability. The
optimized route removed host materialization of `point_ids` and `core_flags`
from the component signature, kept the same Embree/OptiX contract, and received
Claude/Codex review closure.

## Why This Does Not Release V3

This row does not override the serious same-hardware V2.14 vs Phoenix V3
paired run:

```text
same_metric_comparison_count: 52
overall_geomean_v3_speedup_vs_v2_14: 1.0117790403434224
apps_with_geomean_gt_1_05: 1
apps_with_geomean_lt_0_95: 2
release_consideration_eligible: false
```

The old no-go packet remains important context: the large rows are still
limited by the Numba continuation, and the old 1483.603x route-mixed row is not
public evidence.

## Limits

- This is a component-signature route, not full DBSCAN label publication.
- It is not RTDBSCAN paper reproduction.
- It is not broad V3-over-V2.x performance evidence.
- It is not a full application benchmark claim.
- Large-row correctness is OptiX/Embree intra-run canonical component-signature
  agreement, not independent CPU reference validation.
- The dataset is synthetic zero-noise four-cluster `clustered3d`.
- At 262,144 and 524,288 points, the Numba continuation still dominates wall
  time.

## Gap-1 Boundary

The component_union row does not complete Gap 1. It proves one useful
component-signature continuation route, but it is not yet the productized
prepared execution/session runner shared across multiple Set-A probes.

For the next all-app scorecard, RTDBSCAN is a Set-A candidate only if the shared
`component_union` or productized execution path is the measured source of the
win. Materializing Embree neighbor rows remain Set-B controls. Classification
must be frozen before the run.

## Forbidden Readings

- Do not claim RTDBSCAN is faster.
- Do not claim full DBSCAN is accelerated end to end.
- Do not claim RTDL reproduces the RTDBSCAN paper.
- Do not claim RT cores accelerate full DBSCAN labels.
- Do not revive the old `1483.603x` route-mixed all-app row as public evidence.
- Do not claim the RT threshold phase alone is the RTDBSCAN app speedup.
- Do not claim this row proves broad V3-over-V2.x speedup.
- Do not claim this row completes Gap 1.

## Next

Keep the component_union row in the current internal surface. Do not spend
Phoenix time on RTDBSCAN app-specific shortcuts or native DBSCAN ABI. If
RTDBSCAN is used next, productize the shared `component_union` / typed-stream
continuation through the prepared execution/session runner and measure it as a
Set-A route.

## Goal-Level Decision Audit

Decision: close RTDBSCAN component_union for Phoenix redo as one retained
row-scoped reusable capability, not as full RTDBSCAN, paper, or V3 release
evidence.

1. Was I foolish?

   No. The decision keeps the reviewed repeat=5 component_union row while
   preserving the old no-go limits and the serious V2.x performance blocker.

2. If yes, what actions made the decision foolish?

   It would be foolish to revive the old 1483.603x route-mixed row, call
   component_signature full DBSCAN labels, or turn a 1.102x-1.236x row-scoped
   range into broad V3 success.

3. Was there another path?

   Delete RTDBSCAN from V3 because the earlier no-go was real. That would ignore
   the later same-contract optimization and review closure.

4. Can I now try a different path?

   Retain exactly one component_union row, document its limits, and only count
   future RTDBSCAN work if it lands in a shared productized continuation/runner
   path.
