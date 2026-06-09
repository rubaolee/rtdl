# Goal4104 - Direct Status Union Preview For Partition Convergence

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4100 showed that the unordered non-skip partition-pair stream is faster than the sorted non-skip stream, but it still materializes a near-pair table and still uses a count pass plus an emit pass.

Goal4104 tests the next larger primitive direction: consume candidate partition-pair status directly on the device and produce the component-size signature without materializing near-pair columns.

The new preview function is:

`build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d`

It is a CuPy preview only. It does not add native ABI and does not change the current recommended RT-DBSCAN route.

## Contract

The direct-status preview records:

- `pair_enumeration = device_direct_status_union`
- `pair_order = not_materialized_direct_status_scan`
- `partition_summary_materialized = false`
- `near_pair_columns_materialized = false`
- `pair_materialization_avoided = true`
- `direct_status_union_used = true`

It returns only the component-size signature. It is therefore an order-insensitive continuation contract, not a replacement for consumers that require ordered pair rows.

## Pod Evidence

Artifact:

`docs/reports/goal4104_direct_status_union_timing_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `08e5836de6281300b3cee18f2849e57cbaa76c7a`
- Tracked worktree dirty: `false`
- Point count: 65,536
- Cell factor: 0.125
- Repeat: 3 measured runs after 1 warmup

## Timing Versus Goal4100-Style Materialized Unordered Path

| Profile | Direct status union median (s) | Materialized unordered median (s) | Speedup | Partitions | Non-skip pairs | Union iterations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.092342 | 0.114393 | 1.239x | 16,772 | 10,960,581 | 2 |
| road3d | 0.066645 | 0.100519 | 1.508x | 18,028 | 6,830,362 | 2 |
| ngsim_dense | 0.124214 | 0.162784 | 1.311x | 60,094 | 11,585,223 | 2 |

The result is the first evidence in this RT-DBSCAN partition-convergence chain where removing the row table itself wins across all three profiles. Goal4100 improved the emitted row stream; Goal4104 shows that the stronger design is to avoid emitting that stream when the continuation only needs a component signature.

## Interpretation

This is still not a route promotion. It proves a direction:

- direct device status consumption is better than another row-stream cleanup;
- the component continuation can remain app-agnostic because it is expressed as fixed-radius partition status plus grouped union;
- a future promoted primitive should expose a generic direct grouped-union continuation, not a DBSCAN-specific native engine path.

The next useful measurement is the stricter one: compare direct-status component signatures against the current recommended RTDL/OptiX grouped stream plus Numba continuation at the same profiles and reuse windows. If that wins, then route promotion can be reconsidered. If not, the direct-status path remains a promising internal preview.

## Boundary

This report does not promote `partition_convergence_hybrid` as a default route and does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.
