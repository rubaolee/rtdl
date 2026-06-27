# Goal1188 Claude Review: Next RTX Pod Gap Analysis

Date: 2026-04-30

Reviewer: Claude (external review)

## VERDICT: ACCEPT

Goal1188 correctly identifies the gaps, preserves the established public-wording
count, properly scopes the timing-only followups, and makes a technically sound
pod-deferral recommendation. All four review questions are answered affirmatively
below.

---

## Q1: Does Goal1188 correctly identify the six public apps still needing public-wording evidence?

**Yes.**

Cross-referencing `docs/v1_0_rtx_app_status.md` and `docs/app_engine_support_matrix.md`,
the 10 reviewed public-wording rows are:

1. `service_coverage_gaps / prepared_gap_summary`
2. `event_hotspot_screening / prepared_count_summary`
3. `outlier_detection / prepared_fixed_radius_density_summary`
4. `dbscan_clustering / prepared_fixed_radius_core_flags`
5. `robot_collision_screening / prepared_pose_flags`
6. `facility_knn_assignment / coverage_threshold_prepared_recentered`
7. `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
8. `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
9. `ann_candidate_search / candidate_threshold_prepared`
10. `barnes_hut_force_app / node_coverage_prepared_rich`

The remaining six NVIDIA RT-core-ready public apps — `database_analytics`,
`graph_analytics`, `road_hazard_screening`, `polygon_pair_overlap_area_rows`,
`polygon_set_jaccard`, and `hausdorff_distance` — each carry
`public_wording_not_reviewed` in `v1_0_rtx_app_status.md`. Goal1188 names exactly
these six as `needs_public_wording_evidence`. The identification is correct.

The gap descriptions are technically precise:

- `database_analytics`: timing just below the 0.1 s review floor; a larger-scale or
  higher repeat-count same-contract run is required before public wording review.
- `graph_analytics`: no explicit same-semantics CPU/Embree baseline defined for the
  `visibility_edges` and native graph-ray paths. BFS orchestration must remain outside
  the claim scope.
- `road_hazard_screening`: no same-contract CPU/Embree baseline scoped to the
  compact summary output (not full GIS/routing); the status table confirms the path
  is `ready_for_rtx_claim_review` but wording remains unreviewed.
- `polygon_pair_overlap_area_rows`: candidate discovery has not been isolated from
  exact area continuation in a public-wording context. Only the candidate-discovery
  sub-path is eligible.
- `polygon_set_jaccard`: chunk-size contract is not yet stable and exact Jaccard
  continuation is separate; a stable chunk-size public wording candidate must be
  defined first.
- `hausdorff_distance`: timing is far below the 0.1 s review floor; larger or
  repeated `directed_threshold_prepared` workload is required while preserving
  oracle-match semantics.

All six entries in `APP_NEXT_ACTIONS` (script lines 16–47) carry non-empty
`next_local` and `next_pod` fields. The validation logic at script lines 96–100
enforces this and the tests confirm it.

---

## Q2: Does it correctly preserve the current 10 reviewed public wording rows and zero blocked wording rows?

**Yes.**

`v1_0_rtx_app_status.md` states "Current reviewed public wording rows after
Goal1126 and Goal1146: `10`." The Goal1186 and Goal1187 two-AI consensus
documents both confirm the row count remains `10` and that no new wording rows
were added by Goal1177 or Goal1184.

Goal1188 reports `reviewed_public_wording_count: 10` and
`blocked_public_wording_count: 0`. Counting the `reviewed_wording` bucket rows in
the full matrix confirms exactly ten entries (service_coverage_gaps,
event_hotspot_screening, facility_knn_assignment, segment_polygon_hitcount,
segment_polygon_anyhit_rows, ann_candidate_search, outlier_detection,
dbscan_clustering, robot_collision_screening, barnes_hut_force_app).
No app carries `public_wording_blocked` status. The counts are correct and
consistent with all upstream consensus documents.

---

## Q3: Does it correctly treat Goal1184 ANN and robot rows as timing-only non-promotion followups?

**Yes.**

`v1_0_rtx_app_status.md` (app_engine_support_matrix RT-core cloud policy section)
states:
- `ann_candidate_search`: "Goal1177 accepted the recovered clean-source ANN timing
  row as timing-only external-review input, and Goal1184 accepted newer Goal1182
  RTX A4500 ANN timing as timing-only external-review input."
- `robot_collision_screening`: "Goal1177 and Goal1184 robot evidence is timing-only."

Goal1188 places both apps in the `reviewed_wording` bucket (their original wording
was reviewed and stands) and separately tracks Goal1184 timing in the
`timing_only_followups` section. The status fields contain the literal phrase
"timing-only" and the `next_action` fields contain "do not promote" — both verified
by the unit tests at lines 48–51.

The handling is correct on both axes: it does not demote the existing reviewed
wording, and it does not promote the Goal1184 timing row into a new or expanded
public wording claim.

---

## Q4: Is the recommendation to defer another pod until same-contract baselines and timing-floor scale choices are prepared technically sound?

**Yes.**

The pod-deferral recommendation is technically sound for all six apps:

- Two apps (`database_analytics`, `hausdorff_distance`) have confirmed timing below
  the 0.1 s review floor. Running a paid pod before resolving the scale/repeat-count
  plan would produce non-reviewable artifacts.
- Two apps (`polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) require an
  explicit contract split between the candidate-discovery sub-path and the exact
  continuation. Running the pod without that split would produce ambiguous timing
  that cannot be scoped to a public claim.
- Two apps (`graph_analytics`, `road_hazard_screening`) require a defined
  same-contract CPU/Embree baseline before any OptiX comparison is meaningful.
  Without the baseline, a cloud batch produces numerator timing but no denominator
  to anchor a speedup ratio.

Batching all six into a single pod (rather than running one at a time) is the right
policy: it avoids multiple paid pod sessions and ensures the baseline/contract
decisions are made coherently before spending cloud budget. The ANN/robot
conditional ("only if their wording contract changes") is the correct gate because
their existing wording is already reviewed and Goal1184 confirmed timing-only
follow-ups do not require a new pod for promotion.

---

## Summary of Findings

| Review question | Finding |
| --- | --- |
| Six apps correctly identified | Yes — exact match to `v1_0_rtx_app_status.md` |
| 10 reviewed / 0 blocked rows preserved | Yes — consistent with Goal1186/Goal1187 consensus |
| Goal1184 ANN/robot as timing-only | Yes — "do not promote" language, `reviewed_wording` bucket preserved |
| Pod deferral technically sound | Yes — each gap has a specific actionable prerequisite |

## Boundary

This review is an external gap-analysis audit only. It does not authorize public
RTX speedup wording, release, tagging, or another pod run.
