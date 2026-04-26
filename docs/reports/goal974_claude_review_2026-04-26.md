---
goal: Goal974 Claude review
date: 2026-04-26
reviewer: Claude (claude-sonnet-4-6)
verdict: ACCEPT
---

# Goal974 Remaining Local Baseline Collection — Claude Review

## Verdict

**ACCEPT** — no blockers found.

## Review Questions

### 1. Were locally available CPU/Embree baselines collected for the six remaining rows?

Yes. The script (`scripts/goal974_remaining_local_baselines.py`) produces exactly 13 artifacts across the six rows:

| Row | Collected baselines |
| --- | --- |
| `road_hazard_screening / road_hazard_native_summary_gate` | `cpu_python_reference`, `embree_same_semantics` |
| `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental` | `cpu_python_reference`, `embree_same_semantics` |
| `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate` | `cpu_python_reference` (only locally runnable) |
| `polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate` | `cpu_python_reference`, `embree_native_assisted_candidate_discovery` |
| `polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate` | `cpu_python_reference`, `embree_native_assisted_candidate_discovery` |
| `graph_analytics / graph_visibility_edges_gate` | `cpu_python_reference_visibility_edges`, `cpu_python_reference_bfs`, `cpu_python_reference_triangle_count`, `embree_graph_ray_bfs_and_triangle_when_available` |

Goal971 JSON confirms all of these as `status: valid`. ✓

### 2. Are there now zero invalid baseline artifacts?

Yes. Goal971 JSON reports `bad_rtx_artifact_count: 0` and every `baseline_checks` entry for these rows shows `status: valid` or `status: missing` — no `invalid` entries anywhere across all 17 rows. The test asserts `invalid_artifact_count == 0`. ✓

### 3. Are the remaining missing baselines correctly limited to PostGIS or OptiX-only evidence?

Yes. Cross-checking Goal971 JSON against the test's `expected_remaining_missing`:

| Row | Remaining missing | Category |
| --- | --- | --- |
| `road_hazard_screening` | `postgis_when_available` | PostGIS |
| `segment_polygon_hitcount` | `postgis_when_available` | PostGIS |
| `segment_polygon_anyhit_rows` | `optix_prepared_bounded_pair_rows`, `postgis_when_available_for_same_pair_semantics` | OptiX + PostGIS |
| `polygon_pair_overlap_area_rows` | `postgis_when_available_for_same_unit_cell_contract` | PostGIS |
| `polygon_set_jaccard` | `postgis_when_available_for_same_unit_cell_contract` | PostGIS |
| `graph_analytics` | `optix_visibility_anyhit`, `optix_native_graph_ray_bfs`, `optix_native_graph_ray_triangle_count` | OptiX only |

Every remaining gap requires either a PostGIS host or an OptiX/RTX-capable GPU. None are locally collectible on a CPU/Embree-only machine. ✓

### 4. Does Goal971 remain conservative with `public_speedup_claim_authorized_count=0`?

Yes. Goal971 JSON shows `"public_speedup_claim_authorized_count": 0` and every one of the 17 rows has `"public_speedup_claim_authorized": false`. The test asserts this explicitly. Additionally, `same_semantics_baselines_complete_count: 7` and `baseline_pending_count: 6` are both consistent with the human-readable report. ✓

### 5. Are any public speedup or whole-app claims over-authorized?

No. All 17 rows show `public_speedup_claim_authorized: false`. Claim scopes are narrow prepared-sub-path claims; `non_claim` fields explicitly exclude whole-app, SQL-engine, full-DBMS, routing, kinematics, and broad graph-system acceleration language. No over-authorization found. ✓

## Summary

All five review questions pass. The 13 locally available baseline artifacts are collected and valid, invalid count is zero, remaining gaps are correctly bounded to PostGIS and OptiX-only evidence, and Goal971 holds at `public_speedup_claim_authorized_count=0` with no over-authorized claims.
