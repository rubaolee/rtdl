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
  `run_summary.phase_timing_seconds.traversal.total_sec`
- Contact manifold:
  `native_collect_elapsed_sec`
- RayDB:
  `metadata.prepared_phase_timing_summary.native_call_wall.total_sec`
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
the eight unchanged declared paths exist in the Goal3976 fresh-helper
current-scale artifact. The two short-row paths for Robot collision and RayDB
are superseded by the Goal3984 resident high-repeat summary contract because
the Goal3976 artifact predates those summary fields.

## Boundary

This is benchmark metadata hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
