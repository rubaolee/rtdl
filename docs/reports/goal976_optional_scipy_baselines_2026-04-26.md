# Goal976 Optional SciPy/Reference-Neighbor Baselines

Status: `ok`

SciPy/reference-neighbor baselines are optional external baselines. These artifacts do not authorize public RTX speedup claims.

- environment: disposable venv `/tmp/rtdl_goal976_scipy_venv`
- SciPy: `1.17.1`
- NumPy: `2.4.4`
- fixed-radius copies: `20000`
- spatial copies: `20000`
- iterations: `10`
- artifacts: `4`

## Result

Goal976 collected the four optional SciPy/reference-neighbor baselines that were still missing after Goal975:

- `outlier_detection / prepared_fixed_radius_density_summary`
- `dbscan_clustering / prepared_fixed_radius_core_flags`
- `service_coverage_gaps / prepared_gap_summary`
- `event_hotspot_screening / prepared_count_summary`

After regenerating Goal836/Goal971:

- Goal836 valid artifacts: `46 / 50`
- Goal836 invalid artifacts: `0`
- Goal836 remaining missing artifacts: `4`
- Goal971 strict same-semantics baseline-complete RTX rows: `15 / 17`
- Goal971 public speedup claims authorized: `0`

Remaining gaps are now OptiX-only artifacts:

- `graph_analytics`: `optix_visibility_anyhit`
- `graph_analytics`: `optix_native_graph_ray_bfs`
- `graph_analytics`: `optix_native_graph_ray_triangle_count`
- `segment_polygon_anyhit_rows`: `optix_prepared_bounded_pair_rows`

The spatial SciPy artifacts validate against existing Embree compact-summary semantics instead of the O(N*M) CPU row path at 20k-copy scale. This keeps the optional baseline bounded and same-semantics without turning the collector into a huge CPU brute-force job.

| App | Baseline | Artifact | Status |
|---|---|---|---|
| `outlier_detection` | `scipy_or_reference_neighbor_baseline_when_used_in_app_report` | `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json` | `ok` |
| `dbscan_clustering` | `scipy_or_reference_neighbor_baseline_when_used_in_app_report` | `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json` | `ok` |
| `service_coverage_gaps` | `scipy_baseline_when_available` | `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_scipy_baseline_when_available_2026-04-23.json` | `ok` |
| `event_hotspot_screening` | `scipy_baseline_when_available` | `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_scipy_baseline_when_available_2026-04-23.json` | `ok` |
