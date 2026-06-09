# Goal4108 - Prepared Direct Status Union Reuse Timing

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4105 showed why the naive app-level direct-status route could not be promoted: it rebuilt point rows and partition columns every call, so it lost to the current RTDL/OptiX grouped-stream plus Numba route even though Goal4104 had already shown direct-status consumption was faster inside the resident runtime shape.

Goal4108 adds and times the missing reuse surface:

`prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(...)`

`run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(...)`

The handle prepares point coordinates, partition keys, offsets, counts, point ordinals, and partition AABBs once. It does not prepare or store near-pair columns.

## Pod Evidence

Artifact:

`docs/reports/goal4108_prepared_direct_status_reuse_timing_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `fa7386ce30fac2c226427b54b916842a19e5d08e`
- Tracked worktree dirty: `false`
- Point count: 65,536
- Cell factor: 0.125
- Repeat: 3 measured runs after 1 warmup

## Result

| Profile | Prepare (s) | Prepared replay median (s) | One-shot direct median (s) | Current route median (s) | Replay vs one-shot | Replay vs current | 3-run amortized prepared (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.219194 | 0.050407 | 0.090821 | 0.189148 | 1.802x | 3.752x | 0.123477 |
| road3d | 0.042184 | 0.028225 | 0.069578 | 0.131184 | 2.465x | 4.648x | 0.042295 |
| ngsim_dense | 0.041945 | 0.085393 | 0.127058 | 0.103054 | 1.488x | 1.207x | 0.099378 |

All rows produced the same component-size signature as the one-shot direct-status path and the current route.

## Interpretation

This is the first RT-DBSCAN partition-convergence result in the direct-status chain that fixes the Goal4105 setup-boundary objection.

- Goal4104: direct device status beats materialized unordered partition-pair rows inside the resident runtime shape.
- Goal4105: naive app-level direct status loses because setup and packing repeat every call.
- Goal4108: prepared direct status reuses resident point/partition columns and wins as a replay path across all three profiles.

The strongest win is the replay path. The three-run amortized result also beats the current route median in this artifact, but `ngsim_dense` is close enough that this should remain a preview until a route-level prepared benchmark repeats it under a promoted app mode.

## Boundary

This report does not promote `partition_convergence_hybrid` as a default route. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.
