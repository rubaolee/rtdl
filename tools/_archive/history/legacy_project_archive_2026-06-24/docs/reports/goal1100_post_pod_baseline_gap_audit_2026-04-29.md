# Goal1100 Post-Pod Baseline Gap Audit

Date: 2026-04-29

Valid: `true`

Goal1100 audits baseline readiness after Goal1098/Goal1099. It does not authorize public RTX speedup claims. Both audited apps still need same-current-contract baseline review before public wording.

## Summary

| Metric | Value |
| --- | ---: |
| `row_count` | `2` |
| `rtx_correct_count` | `2` |
| `public_speedup_claim_ready_count` | `0` |
| `baseline_missing_or_partial_count` | `2` |

## Rows

| App | Path | RTX correct | Baseline status | Public claim ready | Next action |
| --- | --- | --- | --- | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `True` | `partial_cpu_oracle_present_needs_fastest_non_optix_phase_baseline` | `False` | Produce a same current-contract fastest non-OptiX phase-separated baseline, preferably Embree or CPU oracle with input/prepare/query/postprocess phases separated and reviewed against the recentered RTX artifact. |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `True` | `current_contract_baseline_missing` | `False` | Produce a same current-contract non-OptiX baseline pair: one validated depth-8 small-scale row matching the RTX validation contract and one large timing row matching the 20M timing contract, then run 2+ AI review before public wording. |

## Boundary

Goal1100 audits baseline readiness after Goal1098/Goal1099. It does not authorize public RTX speedup claims. Both audited apps still need same-current-contract baseline review before public wording.
