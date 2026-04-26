# Goal975 Claude Review — 2026-04-26

**Verdict: ACCEPT**

Reviewer: Claude Sonnet 4.6
Date: 2026-04-26

---

## Review Dimensions

### 1. Collector is bounded

PASS.

The `collect()` function in `scripts/goal975_linux_postgis_remaining_baselines.py` targets exactly five hard-coded `(app, path_name, baseline_name)` triples. The `copies` and `repeats` parameters are bounded integers (defaults 256 and 3). The `_repeat()` loop iterates exactly `repeats` times. `_road_postgis_once()` opens and closes its own connection and runs `DROP SCHEMA IF EXISTS` before `CREATE SCHEMA`, so successive repeats are independent and do not accumulate state. No unbounded iteration, no open-ended result sets.

### 2. Artifacts do not authorize public RTX speedup claims

PASS.

`collect()` embeds an explicit `boundary` key in its return payload: "PostGIS is an external same-semantics baseline. These artifacts do not authorize public RTX speedup claims." The Markdown report (`goal975_linux_postgis_remaining_baselines_2026-04-26.md`) carries this boundary statement in its preamble.

`goal971_post_goal969_baseline_speedup_review_package_2026-04-26.md` confirms `public speedup claims authorized: 0` across all 17 rows, and the test `test_goal971_stays_conservative_after_partial_baseline_collection` asserts `payload["public_speedup_claim_authorized_count"] == 0`, binding this property to a regression gate.

### 3. PostGIS gaps are closed correctly

PASS.

Goal836 (`goal836_rtx_baseline_readiness_gate_2026-04-23.md`) shows the following five rows as `ok` after Goal975:

| App | Path | Status |
|---|---|---|
| `road_hazard_screening` | `road_hazard_native_summary_gate` | ok |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | ok |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | ok (for postgis baseline) |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | ok |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | ok |

Valid artifact count increased from 37 to 42 (five new), invalid artifact count remains 0. The collector's five targets exactly correspond to what was missing; no over-collection or under-collection.

### 4. Remaining gaps stated honestly

PASS.

Goal836 reports 8 remaining missing artifacts across 6 rows. The Goal975 report correctly identifies and categorizes all of them:

- **4 optional SciPy/reference-neighbor baselines** (`outlier_detection`, `dbscan_clustering`, `service_coverage_gaps`, `event_hotspot_screening`) — conditionally required only when app uses the corresponding SciPy path.
- **3 graph OptiX baselines** (`graph_analytics`: `optix_visibility_anyhit`, `optix_native_graph_ray_bfs`, `optix_native_graph_ray_triangle_count`) — RT hardware not yet exercised for this path.
- **1 OptiX bounded pair-row baseline** (`segment_polygon_anyhit_rows`: `optix_prepared_bounded_pair_rows`) — RTX artifact exists; same-semantics baseline pending.

The Goal975 report states: "Remaining gaps are no longer PostGIS gaps." This is accurate. Goal836 overall status remains `needs_baselines`, which is correct — 8 missing artifacts remain.

Goal971 correctly classifies the two `baseline_pending` rows (`graph_analytics`, `segment_polygon_anyhit_rows`) and four `active_gate_complete_but_full_baseline_review_limited` rows. No row is falsely promoted to `same_semantics_baselines_complete`.

### 5. Tests match the new state

PASS.

`goal975_linux_postgis_remaining_baselines_test.py`:
- `test_collector_targets_exact_remaining_postgis_baselines` verifies all five `(app, path_name, baseline_name)` triples appear in the Goal835 catalog with the correct `required_baselines` membership, and that artifact filenames follow the expected convention. Runnable without a PostGIS connection.
- `test_phase_helpers_cover_required_gate_fields` verifies all three phase helpers (`_segpoly_phase`, `_anyhit_phase`, `_polygon_phase`) emit the exact field sets required by their respective gate schemas.

`goal974_remaining_local_baselines_test.py`:
- `test_remaining_baselines_are_valid_after_linux_postgis_collection` asserts 0 invalid artifacts and that the exact set of still-missing baselines is the 8-item set documented in Goal836 and Goal971. Any regression (new invalid, false completion, uncounted gap) would fail this test.
- `test_goal971_stays_conservative_after_partial_baseline_collection` asserts `same_semantics_baselines_complete_count == 11`, `baseline_pending_count == 2`, and `public_speedup_claim_authorized_count == 0`. These three assertions together pin the claim-authorization boundary against regressions.

Test expectations are in exact correspondence with the live artifact state, with no discrepancy between what the tests expect to be missing and what Goal836/Goal971 report as missing.

---

## Summary

All five review dimensions pass. The collector is bounded, produces no false speedup authorization, closes exactly the right PostGIS gaps, characterizes remaining gaps accurately by type, and is covered by tests that will catch regressions in all of the above.
