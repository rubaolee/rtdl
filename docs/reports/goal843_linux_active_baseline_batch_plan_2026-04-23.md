# Goal843 Linux Active Baseline Batch

Status: `plan_only`

This batch targets the remaining active Linux-only baselines: live PostgreSQL DB compact summaries and large exact robot pose-count validation. It does not promote deferred apps or authorize speedup claims.

## Summary

- selected actions: `4`
- failures: `0`
- statuses: `linux_postgresql_required, linux_preferred_for_large_exact_oracle`

## Actions

| App | Path | Baseline | Status | Artifact |
|---|---|---|---|---|
| database_analytics | prepared_db_session_sales_risk | postgresql_same_semantics_on_linux_when_available | linux_postgresql_required | docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_postgresql_same_semantics_on_linux_when_available_2026-04-23.json |
| database_analytics | prepared_db_session_regional_dashboard | postgresql_same_semantics_on_linux_when_available | linux_postgresql_required | docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_postgresql_same_semantics_on_linux_when_available_2026-04-23.json |
| robot_collision_screening | prepared_pose_flags | cpu_oracle_pose_count | linux_preferred_for_large_exact_oracle | docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_cpu_oracle_pose_count_2026-04-23.json |
| robot_collision_screening | prepared_pose_flags | embree_anyhit_pose_count_or_equivalent_compact_summary | linux_preferred_for_large_exact_oracle | docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json |

## Commands

### database_analytics / postgresql_same_semantics_on_linux_when_available

```bash
python3 scripts/goal842_postgresql_db_prepared_baseline.py --scenario sales_risk --copies 20000 --iterations 10 --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_postgresql_same_semantics_on_linux_when_available_2026-04-23.json
```

### database_analytics / postgresql_same_semantics_on_linux_when_available

```bash
python3 scripts/goal842_postgresql_db_prepared_baseline.py --scenario regional_dashboard --copies 20000 --iterations 10 --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_postgresql_same_semantics_on_linux_when_available_2026-04-23.json
```

### robot_collision_screening / cpu_oracle_pose_count

```bash
python3 scripts/goal839_robot_pose_count_baseline.py --backend cpu --pose-count 200000 --obstacle-count 1024 --iterations 3 --output-json docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_cpu_oracle_pose_count_2026-04-23.json
```

### robot_collision_screening / embree_anyhit_pose_count_or_equivalent_compact_summary

```bash
python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 200000 --obstacle-count 1024 --iterations 3 --output-json docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json
```
