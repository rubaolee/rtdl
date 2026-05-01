# Goal973 Deferred Decision Baselines

Date: 2026-04-26

## Scope

Goal973 collects same-semantics local baselines for deferred RTX-ready decision
rows that do not need another cloud pod:

- `facility_knn_assignment / coverage_threshold_prepared`
- `hausdorff_distance / directed_threshold_prepared`
- `ann_candidate_search / candidate_threshold_prepared`
- `barnes_hut_force_app / node_coverage_prepared`

Each row now has:

- `cpu_oracle_same_semantics`
- `best_available_non_optix_backend_same_semantics`

The non-OptiX backend is Embree for all four rows.

## Collected Artifacts

```text
docs/reports/goal835_baseline_facility_knn_assignment_coverage_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_facility_knn_assignment_coverage_threshold_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_hausdorff_distance_directed_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_hausdorff_distance_directed_threshold_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_ann_candidate_search_candidate_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_ann_candidate_search_candidate_threshold_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_barnes_hut_force_app_node_coverage_prepared_cpu_oracle_same_semantics_2026-04-23.json
docs/reports/goal835_baseline_barnes_hut_force_app_node_coverage_prepared_best_available_non_optix_backend_same_semantics_2026-04-23.json
```

## Scale Notes

| App | Scale |
| --- | --- |
| `facility_knn_assignment` | `copies=20000`, `iterations=10` to satisfy the fixed Goal835 scale. |
| `hausdorff_distance` | `copies=4096`, `iterations=3`; Goal835 has no fixed scale for this row, and `copies=20000` was too expensive locally. |
| `ann_candidate_search` | `copies=20000`, `iterations=3`; Goal835 has no fixed scale. |
| `barnes_hut_force_app` | `body_count=4096`, `iterations=3`; Goal835 has no fixed scale. |

## Post-Collection State

Goal836 now reports these four rows as `ok`.

Goal971 regenerated state:

```text
strict same-semantics baseline-complete rows: 7
active-gate limited rows: 4
baseline-pending rows: 6
public speedup claims authorized: 0
```

Remaining baseline-pending rows are graph, road hazard, segment/polygon
hitcount, segment/polygon bounded rows, polygon pair overlap, and polygon set
Jaccard.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal973_deferred_decision_baselines_test \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal846_active_rtx_claim_gate_test

OK
```

## Verdict

`ACCEPT` from Codex.

The four local decision rows now have complete same-semantics baseline evidence
for separate speedup review. No public speedup wording is authorized.
