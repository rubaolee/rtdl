# Goal1005 Post-A5000 Speedup Candidate Consensus

Date: 2026-04-26

## Verdict

Status: `ACCEPT`.

Goal1005 correctly replaces stale Goal978/Goal969-derived speedup-candidate classification with classification based on the final Goal1004 RTX A5000 v2 artifact bundle.

No public speedup claim is authorized by this goal.

## Result

- Rows audited: `17`
- Candidate rows for later 2-AI public-claim review: `8`
- Internal-only rows: `1`
- Rejected current public-speedup rows: `8`
- Public speedup claims authorized: `0`

## Candidate Rows

These rows are candidates only. They still need separate claim-wording review before public use.

- `robot_collision_screening / prepared_pose_flags`
- `outlier_detection / prepared_fixed_radius_density_summary`
- `dbscan_clustering / prepared_fixed_radius_core_flags`
- `service_coverage_gaps / prepared_gap_summary`
- `facility_knn_assignment / coverage_threshold_prepared`
- `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
- `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
- `ann_candidate_search / candidate_threshold_prepared`

## Non-Candidate Rows

- `event_hotspot_screening / prepared_count_summary` is internal-only because the margin is below the 20% candidate threshold.
- `database_analytics` rows are rejected for current public speedup claims because Embree is faster in the current same-semantics evidence.
- `road_hazard_screening`, `graph_analytics`, `hausdorff_distance`, `barnes_hut_force_app`, and the two polygon-native-assisted rows are rejected for current public speedup claims under the final A5000 evidence.

## Review Trail

- Codex local tests: `tests.goal1005_post_a5000_speedup_candidate_audit_test` passed.
- Claude external review: `ACCEPT`; saved at `docs/reports/goal1005_claude_external_review_2026-04-26.md`.
- Gemini external review: `ACCEPT`; saved at `docs/reports/goal1005_gemini_external_review_2026-04-26.md`.

Gemini's review is treated as a weak secondary signal because it explicitly said it did not deeply inspect script logic or parse complex data. Claude's review is the substantive external consensus signal.

## Remediation From Review

Claude identified two non-blocking cleanup items:

- remove an unused import,
- harden `_find_result` so multi-result artifacts cannot silently fall back to the first row when the app label does not match.

Both changes were applied, and the Goal1005 tests still pass.

## Boundary

The accepted claim is:

> Goal1005 classifies final RTX A5000 v2 app-gate artifacts into candidate, internal-only, and rejected current-speedup categories using same-semantics baseline timing evidence.

The accepted claim is not:

- public speedup authorization,
- whole-app acceleration authorization,
- release authorization,
- or permission to use the candidate rows in front-page/docs wording without another 2-AI claim wording review.
