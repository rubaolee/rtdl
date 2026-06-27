# V4 Goal4754 Final RT-Core Matrix Analysis

Status: `analysis_complete_not_release_authorization`

Primary denominator: NVIDIA OptiX/RT-core rows only. Embree is not used as a primary denominator.

| app | V2.14 hot s | V3 hot s | V4 hot s | V4/V2 hot | V4/V3 hot | V4/V2 wall | V4/V3 wall | class | metric source |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `rt_dbscan` | 1.53385 | 1.52694 | 1.53716 | 0.997848 | 0.993353 | 1.07979 | 1.07132 | `parity_or_control` | prepared_runner_median_or_adapter_run_sec |
| `raydb_style` | 0.00552286 | 0.00564324 | 0.00509915 | 1.08309 | 1.1067 | 1.08309 | 1.1067 | `parity_or_control` | prepared_iteration_wall_summary.median_sec |
| `triangle_counting` | 0.000774041 | 0.000163548 | 0.000168752 | 4.58686 | 0.96916 | 0.00297791 | 0.7924 | `v4_regression_vs_v3` | timing_ms.query_median_ms; wall=phase_split_ms.one_shot_backend_estimate_ms |
| `librts_spatial_index` | 0.387125 | 0.38636 | 0.385867 | 1.00326 | 1.00128 | 0.95309 | 0.970504 | `parity_or_control` | repeat_protocol.query_sec_median |
| `hausdorff_xhd` | 9.01373 | 9.85597 | 9.47496 | 0.951321 | 1.04021 | 0.95689 | 0.986016 | `v4_regression_vs_v2` | threshold repeat_protocol.measured_query_total_sec |
| `robot_collision` | 0.00237544 | 0.00231845 | 0.00233751 | 1.01623 | 0.991848 | 1.01623 | 0.991848 | `parity_or_control` | tail_medians.total_run_seconds with no_probe_reference |
| `contact_manifold` | 0.00636027 | 0.00638194 | 0.00552156 | 1.1519 | 1.15582 | 0.714607 | 0.729817 | `parity_or_control` | generic_aabb_broadphase+collect_k+python_exact_refinement |
| `rtnn` | 0.000974745 | 0.00097857 | 0.000961248 | 1.01404 | 1.01802 | 0.000829326 | 0.00083812 | `parity_or_control` | V4 timing_sec.hot_query_median; old runner_payload.elapsed_median_sec |
| `spatial_rayjoin` | 7.11419e-05 | 6.86981e-05 | 7.74413e-05 | 0.918655 | 0.887098 | 0.918655 | 0.887098 | `v4_regression_vs_v2` | repeat_protocol.measured_query_total_sec |
| `barnes_hut` | 31.5287 | 0.111805 | 0.112206 | 280.99 | 0.996424 | 163.705 | 0.678794 | `material_v4_over_v2_candidate` | medians.hot_seconds |

## Summary

- material candidate apps: `['barnes_hut']`
- regression apps: `['triangle_counting', 'hausdorff_xhd', 'spatial_rayjoin']`
- V4/V2.14 hot geomean: `2.07076`
- all rows have V2/V3/V4: `True`
- Embree primary denominator used: `False`

## Non-Authorization

This analysis does not authorize release, broad public speedup wording, or whole-app high-performance claims.
