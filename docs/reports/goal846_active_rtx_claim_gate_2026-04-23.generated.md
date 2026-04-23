# Goal846 Active RTX Claim Gate

Status: `ok`

This gate is for active OptiX claim-review readiness only. It counts mandatory active same-semantics baselines and explicitly excludes optional reference baselines and deferred app rows. It does not authorize a public RTX speedup claim by itself.

## Summary

- active rows checked: `5`
- mandatory active baseline artifacts: `12`
- valid mandatory artifacts: `12`
- missing mandatory artifacts: `0`
- invalid mandatory artifacts: `0`
- skipped optional/deferred artifacts: `2`

## Row Readiness

| App | Path | Status | Mandatory Valid | Mandatory Missing | Mandatory Invalid | Skipped Optional/Deferred |
|---|---|---|---:|---:|---:|---:|
| database_analytics | prepared_db_session_sales_risk | ok | 3 | 0 | 0 | 0 |
| database_analytics | prepared_db_session_regional_dashboard | ok | 3 | 0 | 0 | 0 |
| outlier_detection | prepared_fixed_radius_density_summary | ok | 2 | 0 | 0 | 1 |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | 2 | 0 | 0 | 1 |
| robot_collision_screening | prepared_pose_flags | ok | 2 | 0 | 0 | 0 |

## Blocking Gaps

## Non-Blocking Exclusions

### outlier_detection / prepared_fixed_radius_density_summary

- `scipy_or_reference_neighbor_baseline_when_used_in_app_report` excluded from this gate (collection status: `optional_dependency_or_reference_required`, artifact status: `missing`)

### dbscan_clustering / prepared_fixed_radius_core_flags

- `scipy_or_reference_neighbor_baseline_when_used_in_app_report` excluded from this gate (collection status: `optional_dependency_or_reference_required`, artifact status: `missing`)

