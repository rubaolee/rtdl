# Goal976 Claude Review — 2026-04-26

**Verdict: ACCEPT**

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-26

---

## Checklist

### 1. Collector is bounded

PASS. `collect()` iterates exactly two fixed-radius apps and two spatial apps, writing exactly four artifacts. The top-level `boundary` field reads: *"SciPy/reference-neighbor baselines are optional external baselines. These artifacts do not authorize public RTX speedup claims."* The function produces no side-effects beyond writing the four named artifact files and the two report files. No unbounded loops, no recursive collection.

### 2. Four SciPy/reference-neighbor artifacts are valid and same-semantics

PASS on all four.

| App | Path | status | correctness_parity | matches_reference | authorizes_public_speedup_claim |
|---|---|---|---|---|---|
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `ok` | `true` | `true` | `false` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `ok` | `true` | `true` | `false` |
| `service_coverage_gaps` | `prepared_gap_summary` | `ok` | `true` | `true` | `false` |
| `event_hotspot_screening` | `prepared_count_summary` | `ok` | `true` | `true` | `false` |

Same-semantics contracts are correctly scoped:
- Fixed-radius pair: summary-level comparison (`threshold_reached_count / core_count`) matches the compact outlier/DBSCAN contract. Outlier uses exact row tuple comparison; DBSCAN uses summary-level comparison to handle valid ordering differences in core-flag assignment. Both are documented in `claim_limit`.
- Spatial pair: SciPy rows are reduced to the same compact summary type used by the RTX path before comparison (see §3 below).

### 3. Spatial validation choice using Embree compact summaries is honest

PASS. For both spatial apps the code:
1. Runs SciPy and reduces rows to the compact summary (`_service_summary_from_rows` / `_event_summary_from_rows`).
2. Runs the Embree compact-summary path as the reference (`_run_embree_gap_summary` / `_run_embree_count_summary`) and reduces it identically (`_service_summary_from_count_rows` / `_event_summary_from_count_rows`).
3. Compares the two compact summaries.

The rationale is stated in both the code notes and the artifact JSON notes: *"The parity reference uses Embree compact summary to avoid the O(N*M) CPU row path at 20k-copy scale."* The `reference_backend` field in each artifact's `validation` object explicitly names `"embree_gap_summary"` and `"embree_count_summary"` respectively. No claim is made that SciPy was compared against a brute-force row enumeration — the validation method is fully described. This is an honest, reproducible parity check bounded to the documented compact-summary semantics.

Minor note: the spatial artifact `required_phase_coverage` schema retains the OptiX-named slots (`optix_prepare`, `optix_query`) because the spatial app schema is shared across backends. The `source_backend: "scipy_ckdtree"` field disambiguates clearly; `optix_prepare` is `0.0` and `optix_query` holds the SciPy query timing. This reuse is consistent with the established schema and causes no confusion.

### 4. Remaining gaps are only OptiX-only artifacts

PASS. Goal836 report (regenerated after Goal976) shows:

- Valid: 46 / 50 artifacts
- Invalid: 0
- Missing: 4 — all in two deferred rows:
  - `graph_analytics / graph_visibility_edges_gate`: `optix_visibility_anyhit`, `optix_native_graph_ray_bfs`, `optix_native_graph_ray_triangle_count`
  - `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`: `optix_prepared_bounded_pair_rows`

All four missing artifacts are OptiX-native baselines requiring GPU hardware that is not locally available. No non-OptiX artifact is missing. Goal971 confirms exactly two `rtx_artifact_ready_baseline_pending` rows corresponding to these two apps. Goal974 test enforces this set precisely.

### 5. No public RTX speedup claims authorized

PASS. Zero public speedup claims at every layer:
- All four artifact JSON files: `"authorizes_public_speedup_claim": false`
- Collector: `boundary` string explicitly denies authorization
- Goal971 package: `"public_speedup_claim_authorized_count": 0`
- Goal836 gate: status `needs_baselines` (OptiX gaps still present)
- Goal971 test: asserts `public_speedup_claim_authorized_count == 0`
- Goal974 test: asserts `public_speedup_claim_authorized_count == 0`

The Goal971 report's claim-boundary section correctly states that `same_semantics_baselines_complete` still requires separate 2-AI review before public speedup wording.

### 6. Tests match the new state

PASS on all three test files.

**goal976_optional_scipy_baselines_test.py**
- `test_collector_targets_remaining_optional_scipy_baselines`: Verifies all four (app, path_name, baseline) tuples resolve to rows where the baseline name is listed in `required_baselines`, and that the artifact filename follows the `goal835_baseline_<app>_<path_name>_<baseline>_2026-04-23.json` convention. ✓
- `test_fixed_radius_scipy_artifact_schema_without_importing_scipy`: Unit-tests the summary helper functions (`_outlier_summary`, `_dbscan_summary`) against known inputs. ✓

**goal974_remaining_local_baselines_test.py**
- `test_remaining_baselines_are_valid_after_linux_postgis_collection`: Asserts 0 invalid artifacts and exactly the four OptiX-only missing baselines across the two expected rows. Consistent with Goal836 report and Goal976 collection outcome. ✓
- `test_goal971_stays_conservative_after_partial_baseline_collection`: Asserts `same_semantics_baselines_complete_count == 15`, `baseline_pending_count == 2`, `public_speedup_claim_authorized_count == 0`. Matches Goal971 report exactly. ✓

**goal971_post_goal969_baseline_speedup_review_package_test.py**
- `test_package_covers_all_goal969_rtx_rows_without_speedup_overclaim`: 17 rows, 17 RTX-ready, 0 bad, 0 speedup claims, boundary string present. ✓
- `test_baseline_classification_is_conservative`: Individual row spot-checks for `outlier_detection`, `dbscan_clustering`, `event_hotspot_screening` assert `same_semantics_baselines_complete`; `graph_analytics` asserts `rtx_artifact_ready_baseline_pending`. All consistent with Goal976 filling the four SciPy slots. ✓
- `test_cli_writes_json_and_markdown`: Integration test confirming 17-row JSON output. ✓

---

## Summary

Goal976 correctly fills the four remaining optional SciPy/reference-neighbor baseline slots, leaves the four OptiX-only slots as the sole remaining gaps, holds the public-speedup-claim count at zero, and its tests are coherent with all three report documents. No overclaims, no undocumented validation shortcuts, no collector drift. Nothing blocks acceptance.
