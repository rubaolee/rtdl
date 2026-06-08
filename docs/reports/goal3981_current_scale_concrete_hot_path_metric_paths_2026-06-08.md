# Goal3981: Current Scale Concrete Hot-Path Metric Paths

Date: 2026-06-08

## Purpose

Goal3980 made the current scale-profile timing boundary machine-readable.
Goal3981 removes the remaining placeholder by assigning concrete payload paths
for the representative hot-path metric of every promoted benchmark row.

## Change

`src/rtdsl/current_benchmark_scale_profiles.py` now records concrete paths such
as:

- Hausdorff/X-HD:
  `run_phases.query_fixed_radius_threshold_reached_count_sec`
- RayJoin:
  `representative_hot_path_summary`
- RT-DBSCAN:
  `metadata.prepared_query_repeat_protocol.elapsed_sec_median`
- Robot collision:
  `benchmark_timing_sec.tail_phase_traversal_sec`
- Contact manifold:
  `native_collect_elapsed_sec`
- RayDB:
  `metadata.timings.native_call_wall`
- Barnes-Hut:
  `partner_metadata.prepared_force_repeat_protocol.median_force_kernel_sec`
- LibRTS:
  `run_phases.query_median_sec`
- RTNN:
  `runner_payload.elapsed_median_sec`
- Triangle counting:
  `timing_ms.query_median_ms`

The RayJoin entry is intentionally a composite object path rather than a single
scalar because that benchmark row contains several contract-level hot paths.

## Validation

`tests.goal3981_current_scale_concrete_hot_path_metric_paths_test` checks that
every declared path exists in the Goal3976 fresh-helper current-scale artifact.

## Boundary

This is benchmark metadata hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
