# Goal4065 RT-DBSCAN Prepared Partition-Signature App Mode

Date: 2026-06-09

## Purpose

Goal4062 added an explicit prepared CuPy preview handle for the generic
fixed-radius partition-convergence summary. Goal4065 exposes that same
prepared-handle pattern through the RT-DBSCAN benchmark app as a new explicit
candidate mode:

`partner_cupy_prepared_partition_convergence_component_signature_3d`

This is intentionally an app-runner integration, not a new engine primitive. It
lets a learner or reviewer see the prepared partition-summary replay pattern in
the same CLI they use for other RT-DBSCAN modes.

## Behavior

The new mode:

- prepares the generic `fixed_radius_partition_convergence_summary_3d` stream
  once through
  `prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`;
- reuses that prepared stream through
  `run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(...)`;
- returns a sorted `fixed_radius_graph_component_size_signature_3d`;
- records `prepared_partition_summary_sec`, `component_signature_sec`, and
  `prepared_partition_total_sec` separately;
- refuses `--include-rows`, because it does not materialize Python row dicts or
  one label per point.

## Boundaries

This mode is graph-component-contract-only. It is not full DBSCAN
core/border/noise semantics. It does not use RT cores. It does not promote the
partition-convergence hybrid as a default route. It does not add a native ABI,
does not choose partners automatically, and does not authorize release wording,
public speedup wording, broad RT-core wording, whole-app benchmark wording, or
true-zero-copy wording.

## Validation

Added:

- `tests/goal4065_rt_dbscan_prepared_partition_signature_app_mode_test.py`.

The test verifies:

- app, README, and report all expose the prepared candidate mode;
- `--include-rows` fails before CuPy is required;
- when CuPy is available, the tiny prepared candidate output matches the
  existing graph-component reference signature while preserving all claim
  boundaries.

