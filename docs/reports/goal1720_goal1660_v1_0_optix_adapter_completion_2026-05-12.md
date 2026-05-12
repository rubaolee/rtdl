# Goal1720 Goal1660 v1.0 OptiX Adapter Completion

Date: 2026-05-12

Status: v1.0 OptiX baseline command-shape recovery after Goal1718.

## Context

Goal1718 showed that the current v1.6.11 candidate completed all 28 planned
Goal1660 invocations, but only 4 of 28 v1.0 baseline invocations produced
artifacts. The failures were not pod or native-library failures. They were CLI
shape mismatches: many v1.0 scripts are OptiX-only and do not accept the newer
current-manifest `--backend optix` argument.

The v1.0 script help confirmed that these scripts expose `--mode optix` or
OptiX-only `--mode run`, but no `--backend` argument:

- `scripts/goal811_spatial_optix_summary_phase_profiler.py`
- `scripts/goal887_prepared_decision_phase_profiler.py`
- `scripts/goal933_prepared_segment_polygon_optix_profiler.py`
- `scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py`
- `scripts/goal877_polygon_overlap_optix_phase_profiler.py`
- `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`

## Adapter

The adapter reran the failed v1.0 OptiX rows after dropping only the trailing:

```text
--backend optix
```

from the v1.0 command. It did not adapt or fake v1.0 Embree rows, because the
older scripts do not expose a real Embree selector for those rows.

Raw adapter artifacts:

```text
docs/reports/goal1720_goal1660_v1_0_optix_adapter_raw_2026-05-12.json
docs/reports/goal1720_goal1660_v1_0_optix_adapter_raw_2026-05-12.log
```

The adapter completed:

```text
attempted_count: 12
completed_count: 12
failures: []
```

## Recovered v1.0 OptiX Rows

The adapter produced v1.0 OptiX artifacts for:

| App | Artifact |
| --- | --- |
| `service_coverage_gaps` | `docs/reports/goal1660_v1_0_service_coverage_gaps_optix.json` |
| `event_hotspot_screening` | `docs/reports/goal1660_v1_0_event_hotspot_screening_optix.json` |
| `facility_knn_assignment` | `docs/reports/goal1660_v1_0_facility_knn_assignment_optix.json` |
| `road_hazard_screening` | `docs/reports/goal1660_v1_0_road_hazard_screening_optix.json` |
| `segment_polygon_hitcount` | `docs/reports/goal1660_v1_0_segment_polygon_hitcount_optix.json` |
| `segment_polygon_anyhit_rows` | `docs/reports/goal1660_v1_0_segment_polygon_anyhit_rows_optix.json` |
| `polygon_pair_overlap_area_rows` | `docs/reports/goal1660_v1_0_polygon_pair_overlap_area_rows_optix.json` |
| `polygon_set_jaccard` | `docs/reports/goal1660_v1_0_polygon_set_jaccard_optix.json` |
| `hausdorff_distance` | `docs/reports/goal1660_v1_0_hausdorff_distance_optix.json` |
| `ann_candidate_search` | `docs/reports/goal1660_v1_0_ann_candidate_search_optix.json` |
| `robot_collision_screening` | `docs/reports/goal1660_v1_0_robot_collision_screening_optix.json` |
| `barnes_hut_force_app` | `docs/reports/goal1660_v1_0_barnes_hut_force_app_optix.json` |

Combined with Goal1718's original v1.0 successes, the v1.0 baseline now has:

```text
15 / 15 planned OptiX rows with artifacts
1 / 13 planned Embree rows with artifacts
16 / 28 total planned v1.0 rows with artifacts
```

The remaining unsupported v1.0 Embree rows are not adapted by this goal.

## Verdict

Goal1720 is:

```text
accept-with-boundary
```

Accepted:

- All recoverable v1.0 OptiX command-shape failures were rerun successfully.
- The v1.0 baseline now has artifacts for every planned OptiX row.
- The adapter did not create decorative Embree rows where v1.0 scripts expose
  no real Embree selector.

Boundary:

- The full Goal1660 matrix is still incomplete because 12 non-database v1.0
  Embree rows remain unsupported by the tagged v1.0 scripts.
- Any final cross-version report must compare only same-engine rows with real
  artifacts and must classify unsupported v1.0 Embree rows explicitly.
- No public speedup wording, release/tag action, or v1.8/v2.0 readiness claim is
  authorized by this adapter alone.

Release readiness remains:

```text
needs-more-evidence
```
