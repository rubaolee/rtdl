# Goal1067 Scale-Contract Repair Audit

Date: 2026-04-28

Valid: `true`

Goal1067 is a local scale-contract audit. It does not run OptiX, does not run cloud, does not change public wording, and does not authorize public RTX speedup claims.

## Summary

- scale-contract rows: `2`
- blocked rows: `1`
- pod candidates after review: `1`

## Decisions

| App | Path | Decision | Pod policy | Reason | Next local action |
| --- | --- | --- | --- | --- | --- |
| `hausdorff_distance` | `directed_threshold_prepared` | `blocked_scale_contract_not_repaired` | `no_pod_until_benchmark_contract_changes` | The authored Hausdorff fixture uses an analytic tiled oracle, so raising copies to 20,000 creates 80k logical points per side but does not create a meaningful same-semantics CPU speed baseline. | Do not pod-rerun this as a public speedup candidate. Either keep it as an RTX capability/parity path or design a separate non-analytic threshold-decision benchmark contract with bounded validation. |
| `barnes_hut_force_app` | `node_coverage_prepared` | `pod_candidate_after_review` | `eligible_for_next_pod_after_review` | The 1M-body local dry-run keeps the same node-coverage decision, separates input build from CPU reference, and produces a non-trivial same-semantics CPU reference above the 100 ms scale target. | Add Barnes-Hut 1M node-coverage to the next one-pod batch only after review; keep public wording blocked until real RTX timing, baseline comparison, and 2-AI review exist. |

## Barnes-Hut Recommended Cloud Scale

The only repaired scale-contract candidate is `barnes_hut_force_app / node_coverage_prepared` at `1000000` bodies. This remains a candidate for a future pod batch, not a public claim.
