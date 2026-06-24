# Phoenix V3 RTDBSCAN Component-Union M7 Feasibility

Status: feasibility packet, not M7 promotion.

```text
status: rtdbscan_component_union_m7_feasibility_not_promoted
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

## Verdict

RTDBSCAN/component_union remains internal. The evidence is promising, but no
single row currently satisfies M7.

## All-App Ratio Row

| Field | Value |
| --- | --- |
| Comparison group | `dbscan_cluster_signature` |
| Dataset | `clustered3d` |
| Point count | `8192` |
| Embree primary metric | `25.960369` sec |
| OptiX primary metric | `0.017498` sec |
| OptiX-vs-Embree speedup | `1483.603x` |
| matches_reference | `None` |
| reference_signature | `None` |
| Claim status | `internal_ratio_not_m7_validation_missing` |

This row cannot be promoted because validation is missing in the ratio row.

Supersession note: the later Phoenix same-contract rerun replaces this row for
current public interpretation. That rerun passed validation at serious scales
but only supported small internal OptiX-over-Embree speedups, so RTDBSCAN remains
internal and not M7-promoted.

## M23 Scale Evidence

| Field | Value |
| --- | --- |
| Status | `m49_dbscan_app_uses_compact_component_signature_without_python_row_materialization` |
| Point count | `524288` |
| Copies | `65536` |
| Output mode | `component_signature` |
| Partners | `['cupy', 'numba']` |
| Oracle match | `True` |
| Cluster-size signatures match | `True` |
| Core counts match | `True` |
| Noise counts match | `True` |
| RT-core accelerated | `True` |
| Materializes Python rows | `False` |
| Claim status | `internal_scale_parity_not_m7_no_same_scale_embree_baseline` |

This row cannot be promoted because it has no same-scale Embree baseline.

## M7 Blockers

- `all_app_ratio_row_has_matches_reference_null`
- `all_app_ratio_row_is_8192_points_not_m23_524288_scale`
- `m23_scale_evidence_has_no_same_scale_embree_baseline`
- `component_signature_not_full_dbscan_labels`
- `no_public_component_union_contract`
- `no_final_external_public_row_review`
- `broad_v3_faster_than_v2_claim_authorized_false`

## Next Rerun Requirements

- Use the same component-size signature contract for Embree and OptiX at the same scale.
- Keep validation on or attach an oracle signature artifact, not matches_reference: null.
- Report prepare, hot query, wall, warmup, repeat, partner, and backend separately.
- State component_signature only; do not call it full DBSCAN labels.
- Keep count/core/noise and cluster-size signature parity visible.

## Boundary

Allowed internal reading:

```text
RTDBSCAN has strong internal evidence for component_union: a huge small-scale OptiX/Embree ratio and a separate 524,288-point M23 oracle-matching component signature run.
```

Forbidden public reading:

```text
Do not claim RTDBSCAN V3 is 1483x faster end to end; do not claim paper reproduction; do not claim full DBSCAN acceleration from component signatures.
```

## Goal-Level Decision Audit

Decision: classify RTDBSCAN component_union feasibility without promotion

1. Was I foolish?

   No. The packet separates the strong ratio row from the validated M23 scale row.

2. If yes, what actions made the decision foolish?

   It would be foolish to combine the 1483x all-app ratio with the 524,288-point M23 validation as if they were the same M7 row.

3. Was there another path?

   Run a pod rerun immediately. That is plausible but needs a precise packet first.

4. Can I now try a different path that actually solves the problem?

   Write the feasibility boundary first, then produce a focused same-scale rerun packet if RTDBSCAN remains the next candidate.
