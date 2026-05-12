# Goal1727 Claude Review: Goal1726 Boundary Companion Evidence

**Reviewer**: Claude (claude-sonnet-4-6) — independent review, distinct from Codex and Gemini  
**Date**: 2026-05-12  
**Verdict**: `accept-with-boundary`

---

## Scope

This is an independent Claude review of Goal1726 and the updated Goal1723 consolidation. It was
performed by reading the six companion JSON artifacts, the Goal1726 report, the Goal1723 JSON and
Markdown consolidation, and the test files for both goals. No source files were modified. Test
execution was attempted but blocked by environment permissions; all test assertions were verified
manually against the artifact content.

---

## Check 1: Goal1723 consolidation counts

**Requirement**: 16 artifact pairs, 16 clean parity-or-companion rows, 3 companion resolutions,
0 unresolved boundaries.

Verified directly in `goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json`:

| Field | Required | Observed |
| --- | --- | --- |
| `planned_comparable_rows` | 16 | 16 |
| `artifact_pairs_present` | 16 | 16 |
| `rows_with_clean_parity_or_companion_evidence` | 16 | 16 |
| `rows_with_timing_artifact_boundary_notes` | 3 | 3 |
| `rows_with_companion_resolutions` | 3 | 3 |
| `rows_with_unresolved_boundaries` | 0 | 0 |

**Pass.**

---

## Check 2: Original boundary notes are not erased

**Requirement**: The timing-artifact boundary notes from Goal1723 must remain visible in the
consolidation.

All three rows retain their original `timing_artifact_boundary_notes` array entries. The companion
resolution is recorded alongside, not in place of, the boundary note:

| App/Engine | `timing_artifact_boundary_notes` preserved | `boundary_resolved_by_companion` |
| --- | --- | --- |
| `facility_knn_assignment/optix` | `["skip_validation_true_in_profiler_payload"]` | `true` |
| `robot_collision_screening/optix` | `["validated_false_in_profiler_payload"]` | `true` |
| `polygon_set_jaccard/optix` | `["diagnostic_chunk_config_not_public_safe"]` | `true` |

The 13 non-boundary rows carry empty `timing_artifact_boundary_notes` arrays and
`boundary_resolved_by_companion: false`, which is consistent.

**Pass.**

---

## Check 3: Companion artifact pairs support claimed resolutions

### 3a. `facility_knn_assignment/optix` — `validation_companion_matches_oracle`

The original timing row used `--skip-validation`. The two companion artifacts:

- `goal1726_v1_6_11_facility_validation_companion_optix.json`: `parameters.skip_validation=false`,
  `scenario.result.matches_oracle=true`, `scenario.result.threshold_reached_count=80000`
- `goal1726_v1_0_facility_validation_companion_optix.json`: `parameters.skip_validation=false`,
  `scenario.result.matches_oracle=true`, `scenario.result.threshold_reached_count=80000`

Both companions run the same scenario with validation enabled and produce identical oracle-matching
results. The resolution label `validation_companion_matches_oracle` is accurate.

**Pass.**

### 3b. `robot_collision_screening/optix` — `pose_flags_validation_companion_matches_oracle`

The original timing row had `validated=false`. The two companion artifacts:

- `goal1726_v1_6_11_robot_collision_validation_companion_optix.json`: `validated=true`,
  `matches_oracle=true`, `result.colliding_pose_count=3840`,
  `result.oracle_colliding_pose_count=3840`
- `goal1726_v1_0_robot_collision_validation_companion_optix.json`: `validated=true`,
  `matches_oracle=true`, `result.colliding_pose_count=3840`,
  `result.oracle_colliding_pose_count=3840`

Both companions use `result_mode="pose_flags"` and agree on the colliding-pose count. The
resolution label `pose_flags_validation_companion_matches_oracle` is accurate.

**Pass.**

### 3c. `polygon_set_jaccard/optix` — `public_safe_chunk_companion_passes_parity`

The original timing row used a diagnostic-only chunk configuration. The two companion artifacts:

- `goal1726_v1_6_11_polygon_set_jaccard_public_safe_chunk_optix.json`: `status="pass"`,
  `parity_vs_cpu=true`, `chunk_policy.public_safe=true`, `chunk_copies=1024`,
  `chunk_policy.safe_min=1024`, `chunk_policy.safe_max=4096`
- `goal1726_v1_0_polygon_set_jaccard_public_safe_chunk_optix.json`: `status="pass"`,
  `parity_vs_cpu=true`, `chunk_policy.public_safe=true`, `chunk_copies=1024`,
  `chunk_policy.safe_min=512`, `chunk_policy.safe_max=4096`

Both companions use `policy="public_safe"` and `chunk_copies=1024`, which falls within each
companion's declared safe range. CPU and OptiX digests agree on all summary fields
(`intersection_area`, `jaccard_similarity`, `left_area`, `right_area`, `union_area`).

**Observation**: Both companions report `candidate_count_matches_expected=false` (40,000 observed
vs 60,000 expected), but the candidate_diagnostics note explains this is measured against a
conservative upper-bound model. `positive_pair_count_matches_expected=true` in the v1.6.11
companion, confirming the final output row count matches. The v1.0 companion omits the positive-pair
field but has the same candidate counts and a passing `parity_vs_cpu` result. This does not
undermine the parity conclusion.

**Pass.**

---

## Check 4: No release, tag, or public speedup claim is authorized

All three artifacts explicitly withhold authorization:

- `goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json`:
  `public_claim_authorized=false`, `release_authorized=false`,
  `boundary="Artifact consolidation and companion evidence only; not a speedup or release claim."`
- `goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.md`:
  `Public claim authorized: False`, "release and public wording remain blocked pending final
  release review"
- `goal1726_goal1660_boundary_companion_evidence_2026-05-12.md`: verdict `accept-with-boundary`,
  "This is still artifact hygiene, not release authorization. ... speedup calculations, public
  wording, release tagging, and v1.6.11 publication remain blocked pending final review."

Each of the six companion JSON artifacts carries its own boundary field that explicitly disavows
speedup claims and marks cloud activation as `deferred_until_real_rtx_phase_run_and_review` or
equivalent.

**Pass.**

---

## Test suite structure

`goal1726_goal1660_boundary_companion_evidence_test.py` defines four tests:

1. `test_companion_artifacts_resolve_all_goal1723_boundaries` — checks all six consolidation count
   fields and verifies that each boundary row has `boundary_resolved_by_companion=true` and
   `evidence_pair_ready_without_public_claim=true`. Assertions verified manually against the JSON.
2. `test_facility_and_robot_validation_companions_match_oracle` — checks
   `matches_oracle=true` and `threshold_reached_count=80000` for facility (both versions), and
   `validated=true`, `matches_oracle=true`, `colliding_pose_count=3840` for robot (both versions).
   All four assertions verified against the companion files.
3. `test_jaccard_companions_use_public_safe_chunks` — checks `status="pass"`,
   `parity_vs_cpu=true`, `chunk_policy.public_safe=true`, `chunk_copies=1024` for both Jaccard
   companions. Verified against the companion files.
4. `test_report_keeps_release_blocked` — checks that the Goal1726 report contains
   `accept-with-boundary`, `Unresolved boundaries: \`0\``, and `not release authorization`.
   Verified against the report text.

All assertions pass when checked against the artifact content.

---

## Additional observations

- Thirteen of the 16 rows carry no timing boundary notes and no companion resolutions. Their
  `parity_evidence_clean=true` and `evidence_pair_ready_without_public_claim=true` fields are
  consistent with the artifact content.
- `graph_analytics/optix` and `outlier_detection/optix` have
  `semantic_digest_equal_across_versions=null`. This reflects the absence of a digest comparison
  for those apps and is not a defect in Goal1726.
- `service_coverage_gaps/optix` and `event_hotspot_screening/optix` carry no explicit
  pass/fail status flags in the consolidation, but both have
  `semantic_digest_equal_across_versions=true` and `parity_evidence_clean=true`. This is
  consistent with the timing-only nature of those artifacts.
- The two facility companions and the two robot companions originate from different source commits,
  as expected for a current-vs-v1.0 comparison. The Jaccard companions similarly differ by commit.
- The v1.0 Jaccard companion is missing the `candidate_count_delta_vs_expected` and
  `positive_pair_count_matches_expected` fields present in the v1.6.11 companion. This schema
  difference is minor and does not affect the parity conclusion.

---

## Summary

Goal1726 correctly adds three pairs of companion artifacts that resolve the three timing-artifact
boundary rows identified in Goal1723, without rewriting the original timing artifacts. The
Goal1723 consolidation now accurately reflects 16/16 artifact pairs present, 16/16 rows with
clean parity or companion evidence, 3/3 companion resolutions, and 0 unresolved boundaries, with
release and public-claim authorization explicitly withheld throughout.

**Verdict: `accept-with-boundary`**

The companion evidence is sound for the stated purpose of evidence hygiene. Release, tagging,
public speedup wording, and cloud RTX claims remain blocked and require separate final review.
