# Goal1006 Public RTX Claim Wording Consensus

Date: 2026-04-26

## Verdict

Status: `ACCEPT`.

Goal1006 is accepted as a strict wording gate over the final A5000 speedup candidates. It does not authorize public speedup claims. It only identifies rows mature enough to send to a separate public wording review.

## Result

- Rows audited: `17`
- Goal1005 candidates held for larger-scale repeat: `7`
- Public-review-ready query-phase rows: `1`
- Non-candidate rows: `9`
- Public speedup claims authorized: `0`

## Public-Review-Ready Row

Only one row is ready for a later 2-AI public wording review:

- `service_coverage_gaps / prepared_gap_summary`

Allowed candidate wording for later review:

> On the recorded RTX A5000 run, the bounded `service_coverage_gaps / prepared_gap_summary` query phase was 1.61x faster than the fastest same-semantics non-OptiX baseline for the measured sub-path. This is not a whole-app speedup claim.

This wording is not automatically authorized for the front page. It still needs a separate claim-wording review before public docs can use it.

## Held Rows

The following seven Goal1005 candidate rows are held because their RTX phases are under the 100 ms public-wording floor:

- `robot_collision_screening / prepared_pose_flags`
- `outlier_detection / prepared_fixed_radius_density_summary`
- `dbscan_clustering / prepared_fixed_radius_core_flags`
- `facility_knn_assignment / coverage_threshold_prepared`
- `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
- `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
- `ann_candidate_search / candidate_threshold_prepared`

They may be revisited after larger-scale repeat evidence keeps the comparable RTX phase at or above 100 ms.

## Review Trail

- Codex local tests: `tests.goal1006_public_rtx_claim_wording_gate_test` passed.
- Claude external review: `ACCEPT`; saved at `docs/reports/goal1006_claude_external_review_2026-04-26.md`.
- Gemini external review: `ACCEPT`; saved at `docs/reports/goal1006_gemini_external_review_2026-04-26.md`.

Claude's review is the substantive external review. Gemini's review is a weaker policy-level confirmation but agrees with the conservative gate.

## Boundary

The accepted claim is:

> Goal1006 conservatively filters RTX speedup candidates for later public wording review and leaves only one measured query-phase row ready for that next review step.

The accepted claim is not:

- public speedup authorization,
- whole-app speedup authorization,
- front-page wording authorization,
- or release authorization.
