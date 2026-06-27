# V4 Goal4756 Final RT-Core Matrix Analysis

Status: `analysis_complete_not_release_authorization`

Primary denominator: NVIDIA OptiX/RT-core rows only. Embree is not used as a primary denominator.

| app | V2.14 hot s | V3 hot s | V4 hot s | V4/V2 hot | V4/V3 hot | V4/V2 wall | V4/V3 wall | class | metric source |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `rt_dbscan` | 1.52489 | 1.5173 | 1.52818 | 0.997849 | 0.992885 | 1.10143 | 1.07633 | `parity_or_control` | prepared_runner_median_or_adapter_run_sec |
| `raydb_style` | 0.00567069 | 0.00566274 | 0.0050966 | 1.11264 | 1.11108 | 1.11264 | 1.11108 | `parity_or_control` | prepared_iteration_wall_summary.median_sec |
| `triangle_counting` | 0.000784576 | 0.000183627 | 0.000179939 | 4.36023 | 1.0205 | 0.00316164 | 0.503033 | `material_v4_over_v2_candidate` | timing_ms.query_median_ms; wall=phase_split_ms.one_shot_backend_estimate_ms |
| `librts_spatial_index` | 0.385124 | 0.38638 | 0.385432 | 0.999201 | 1.00246 | 1.08805 | 1.03738 | `parity_or_control` | repeat_protocol.query_sec_median |
| `hausdorff_xhd` | 9.99419 | 9.52183 | 9.68538 | 1.03188 | 0.983114 | 0.945861 | 0.952034 | `parity_or_control` | threshold repeat_protocol.measured_query_total_sec |
| `robot_collision` | 0.00234625 | 0.00230105 | 0.0023009 | 1.01971 | 1.00007 | 1.01971 | 1.00007 | `parity_or_control` | tail_medians.total_run_seconds with no_probe_reference |
| `contact_manifold` | 0.00618469 | 0.00818093 | 0.00554058 | 1.11625 | 1.47655 | 0.744901 | 0.507965 | `parity_or_control` | generic_aabb_broadphase+collect_k+python_exact_refinement |
| `rtnn` | 0.000982534 | 0.000976935 | 0.000954494 | 1.02938 | 1.02351 | 0.000907378 | 0.00090335 | `parity_or_control` | V4 timing_sec.hot_query_median; old runner_payload.elapsed_median_sec |
| `spatial_rayjoin` | 0.0154358 | 0.0155008 | 0.0154353 | 1.00003 | 1.00424 | 1.00003 | 1.00424 | `parity_or_control` | repeat_protocol.measured_query_total_sec |
| `barnes_hut` | 32.1134 | 0.111445 | 0.112229 | 286.142 | 0.993016 | 197.095 | 0.795951 | `material_v4_over_v2_candidate` | medians.hot_seconds |

## Summary

- material candidate apps: `['triangle_counting', 'barnes_hut']`
- regression apps: `[]`
- V4/V2.14 hot geomean: `2.10069`
- all rows have V2/V3/V4: `True`
- Embree primary denominator used: `False`

## Non-Authorization

This analysis does not authorize release, broad public speedup wording, or whole-app high-performance claims.
