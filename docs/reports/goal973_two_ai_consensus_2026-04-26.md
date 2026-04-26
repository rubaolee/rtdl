# Goal973 Two-AI Consensus

Date: 2026-04-26

## Scope

Goal973 collected local same-semantics CPU-oracle and Embree baselines for four
deferred RTX-ready decision rows:

- `facility_knn_assignment / coverage_threshold_prepared`
- `hausdorff_distance / directed_threshold_prepared`
- `ann_candidate_search / candidate_threshold_prepared`
- `barnes_hut_force_app / node_coverage_prepared`

Primary files:

```text
scripts/goal973_deferred_decision_baselines.py
tests/goal973_deferred_decision_baselines_test.py
docs/reports/goal973_deferred_decision_baselines_2026-04-26.md
docs/reports/goal973_claude_review_2026-04-26.md
```

## Codex Verdict

`ACCEPT`.

Goal836 reports all four rows as `ok`, with all required baseline artifacts
valid. Goal971 regenerated to:

```text
strict same-semantics baseline-complete rows: 7
active-gate limited rows: 4
baseline-pending rows: 6
public speedup claims authorized: 0
```

The Hausdorff local scale was reduced to `copies=4096` because the row has no
fixed Goal835 scale and `copies=20000` was too expensive on this Mac. The
reduced scale is recorded in the artifact and report.

## Claude Verdict

`ACCEPT`.

Claude confirmed all four rows have valid CPU-oracle and Embree baselines,
facility uses the required `copies=20000` / `iterations=10` scale, Hausdorff
scale reduction is openly documented, Goal971 remains conservative, and no
public speedup or whole-app claim is over-authorized.

Full review:

```text
docs/reports/goal973_claude_review_2026-04-26.md
```

## Consensus

`ACCEPT`.

Goal973 is closed. The local decision baseline set is materially improved, but
public speedup wording remains unauthorized.

## Remaining Baseline-Pending Rows

- `graph_analytics / graph_visibility_edges_gate`
- `road_hazard_screening / road_hazard_native_summary_gate`
- `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
- `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
- `polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate`
- `polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate`

These are the next local baseline targets before another cloud run.
