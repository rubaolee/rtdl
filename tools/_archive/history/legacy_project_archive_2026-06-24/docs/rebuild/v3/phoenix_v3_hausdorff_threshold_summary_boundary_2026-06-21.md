# Phoenix V3 Hausdorff Threshold-Summary Boundary

Status: `hausdorff_threshold_summary_boundary_not_m7`.

This packet isolates Hausdorff threshold-summary rows as a scoped V3 rebuild
lesson. It is not release evidence and not public speedup wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
full_hausdorff_witness_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: blocked_current_packet
```

## Evidence

Source:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

| Copies | Query OptiX / Embree | Wall OptiX / Embree | Reading |
| ---: | ---: | ---: | --- |
| 16,384 | 2.000x | 0.657x | query win, wall loss |
| 65,536 | 1.595x | 0.965x | query win, near wall parity |
| 262,144 | 1.864x | 1.258x | query win, wall win |

The useful V3 capability is `threshold_summary`: decide whether the Hausdorff
threshold condition is reached. It is not exact witness materialization.

## Best Current Row

The best current row is still a no-go for M7 because it was measured with only
one hot query repeat:

| Field | Value |
| --- | ---: |
| Row ID | `hausdorff_threshold_summary_copies_262144` |
| Comparison group | `hausdorff_threshold_copies_262144` |
| Points in A | 1,048,576 |
| Points in B | 1,048,576 |
| Threshold | 0.4 |
| Embree query median | 10.390607990 s |
| OptiX query median | 5.573154785 s |
| Query OptiX / Embree | 1.864x |
| Embree wall | 21.594328731 s |
| OptiX wall | 17.170473576 s |
| Wall OptiX / Embree | 1.258x |
| Warmup / repeat | 0 / 1 |
| `matches_oracle` | true |
| `oracle_decision_matches` | true |
| `oracle_identity_matches` | true |
| `oracle_within_threshold` | true |

This row is promising threshold-summary evidence, not a public row-scoped
speedup. A future promotion needs a fresh RTX rerun with repeated measurements
and external review.

## Current Blockers

- `threshold_decision_only_not_full_exact_hausdorff_witness`
- `wall_timing_mixed_across_scales`
- `repeat1_no_multi_run_variance_evidence`
- `no_current_rtx_pod_rerun`
- `no_focused_public_row_external_review`
- `must_keep_threshold_scope`

The paired V2.14-vs-current-V3 artifact gives modest V3-over-V2 context:
`hausdorff_xhd` app geomean is 1.062x. That is not broad V3 speedup wording.

## Forbidden Wording

```text
Do not claim Hausdorff V3 is 2x faster end to end.
Do not claim RTDL accelerates full exact Hausdorff witness materialization.
Do not claim threshold_summary is M7-qualified.
Do not claim V3 broadly accelerates Hausdorff over V2.
```

## Tutorial

The current tutorial entry is:

```text
tutorials/current/13_hausdorff_threshold_summary.md
```

It is a rebuild tutorial, not a release tutorial.

## External Review

Fresh external review is blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_hausdorff_threshold_summary_focused_update_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: teach Hausdorff threshold_summary as a scoped boundary, not M7.

1. Was I foolish?

   No. The query-phase signal is useful, but wall timing is mixed and the
   contract is threshold-only.

2. If yes, what actions made the decision foolish?

   It would be foolish to turn the 2.000x query row into a full Hausdorff or
   end-to-end claim.

3. Was there another path that avoided getting stuck on that idea?

   Yes. Rerun the pod immediately, but the current artifact already shows the
   key boundary.

4. Can I now try a different path that actually solves the problem?

   Yes. Expose query versus wall timing and keep threshold-only scope explicit.
