# Goal882 External Review — Barnes-Hut Node Coverage OptiX Sub-Path

**Reviewer:** Claude (external)
**Date:** 2026-04-24
**Branch:** codex/rtx-cloud-run-2026-04-22
**Verdict:** ACCEPT

---

## Scope of Review

Files reviewed from the uncommitted diff:

- `examples/rtdl_barnes_hut_force_app.py`
- `src/rtdsl/app_support_matrix.py`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `scripts/goal824_pre_cloud_rtx_readiness_gate.py`
- `tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py`
- `docs/reports/goal882_barnes_hut_node_coverage_optix_subpath_2026-04-24.md`
- Supporting contract tests (goal690, goal705, goal759, goal803, goal817, goal822, goal824)

---

## Claim Scope Integrity: PASS

The `--optix-summary-mode node_coverage_prepared` path is correctly bounded.
`_run_optix_node_coverage` calls `rt.prepare_optix_fixed_radius_count_threshold_2d` over
quadtree node centers and queries body points with `threshold=1`. The prepared mode
**early-returns** inside `run_app` before the `_run_node_candidates` call, so candidate
generation, opening-rule evaluation, and force reduction are unreachable from this path.
There is zero entanglement between the traversal-backed decision and the Python force path.

The payload's `boundary` and `rtdl_role` fields accurately describe the scope:
"Node-coverage decision only; this is not Barnes-Hut opening-rule evaluation, not
force-vector reduction, and not a fully native N-body solver."

---

## `--require-rt-core` Gate: PASS

`_enforce_rt_core_requirement` now accepts exactly one mode (`node_coverage_prepared`) and
raises `RuntimeError` for all others, including the default `rows` mode. This is the
correct inversion from the previous unconditional raise. The test
`test_require_rt_core_rejects_default_rows` and Goal817's
`test_require_rt_core_rejects_default_optix_row_paths` both cover this boundary.

---

## Oracle Validation: PASS

`node_coverage_oracle` computes the same decision in Python using `math.hypot`, and
`run_app` computes `matches_oracle` by comparing `all_bodies_have_node_candidate` and
`uncovered_body_ids` between the prepared traversal result and the oracle. The comparison
is structurally correct. The `_node_coverage_from_count_rows` function handles missing
rows (no-row → uncovered) via `.get(body.id, {}).get("threshold_reached", 0)`, which
`test_missing_rows_are_uncovered` explicitly exercises.

---

## Manifest Refresh (Goal759 + Goal824): PASS

**Goal759 manifest:**
`barnes_hut_force_app` (plus `hausdorff_distance`, `ann_candidate_search`,
`facility_knn_assignment`) is correctly moved from `excluded_apps` to `deferred_entries`.
Each deferred entry carries:
- `benchmark_readiness: "needs_real_rtx_artifact"` — correct, no RTX artifact exists yet
- `activation_gate` requiring a phase-profiled RTX artifact
- `non_claim` explicitly rejecting opening-rule/force-vector claims

**Goal824 gate:**
The count arithmetic is consistent: 4 apps moved from excluded to deferred, so
deferred +4 (6→10), excluded -4 (12→8), baseline_contract +4 (11→15). The test
`test_manifest_counts_match_expected_values` locks these values.

---

## Contract Test Coverage: PASS

The following contracts are correctly updated:

| Test | Change | Verdict |
|------|--------|---------|
| goal690 performance classification | `barnes_hut_force_app` → `optix_traversal_prepared_summary` | Correct |
| goal705 benchmark readiness | `exclude_from_rtx_app_benchmark` → `needs_real_rtx_artifact` | Correct |
| goal705 prepared summary note | `node_coverage_prepared mode uses OptiX traversal` added | Correct |
| goal803 rt_core maturity | `barnes_hut_force_app` added to `partial` set | Correct |
| goal817 claim gate | Reclassified from `cuda_through_optix`/`needs_rt_core_redesign` to `optix_traversal_prepared_summary`/`rt_core_partial_ready` | Correct |
| goal822 manifest boundary | `barnes_hut_force_app` required in `deferred`, not `active` | Correct |
| goal759 manifest test | Renamed to `test_prepared_decision_apps_are_deferred_not_active`, checks `deferred` not `excluded` | Correct |
| goal824 gate counts | 10 deferred / 8 excluded / 15 baselines | Consistent |

The weakening of Goal822's activation gate assertion from `assertIn("Goal811", ...)` to
`assertIn("Promote only after", ...)` is correct: the new entries reference Goal879–882,
not Goal811.

---

## Unit Test Quality: PASS

`test_optix_node_coverage_mode_uses_prepared_traversal` verifies:
1. `prepare_optix_fixed_radius_count_threshold_2d` is called exactly once
2. Body count matches
3. Radius equals `NODE_DISCOVERY_RADIUS`
4. Threshold is 1
5. `rt_core_accelerated` is `True`
6. `matches_oracle` is `True`
7. `rtdl_role` contains `"node-coverage decision"`
8. `boundary` contains `"not force-vector reduction"`

This test cannot be satisfied by any implementation that skips the prepared traversal
or misroutes the coverage logic.

---

## Minor Observations (Non-Blocking)

**1. `segment_polygon_hitcount` and `segment_polygon_anyhit_rows` in both `REQUIRED_EXCLUDED_APPS` and `REQUIRED_DEFERRED_APPS`**
This overlap also existed before Goal882 (pre-existing pattern, tests pass). The gate
logic handles apps that are simultaneously excluded from active runs and listed as a
deferred path. Not introduced by this goal.

**2. `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` added to `REQUIRED_DEFERRED_APPS`**
Goal882 adds these apps to the required-deferred set even though no new deferred entries
are added for them in this diff. The tests pass, which means these apps already had
deferred entries from a prior goal. Correct, but the rationale is not documented in the
Goal882 diff. Low risk; no action required.

**3. Goal835 baseline JSON files rescaled (copies 2000 → 20000)**
These files (`goal835_baseline_event_hotspot_screening_...` and
`goal835_baseline_service_coverage_gaps_...`) appear in the uncommitted diff but are not
listed in the handoff scope. They are data-only rescalings with consistent structure and
no claim-boundary implications for Goal882. They do not affect the verdict.

---

## Required Fixes

None. No blocking issues found.

---

## Summary

Goal882 adds a correctly scoped, honestly bounded, and adequately tested OptiX traversal
sub-path for the Barnes-Hut node-coverage decision. The traversal claim does not bleed
into opening-rule evaluation or force reduction. The manifest refresh moves four prepared
decision apps from stale exclusions to properly gated deferred entries. All contract tests
are updated consistently and the count arithmetic is verified.

**ACCEPT.**
