# Goal4114 - Prepared Direct Status Repeated App-Route Timing

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4114 runs the route-level repeated app packet requested by Goal4110. It compares:

- explicit prepared direct-status app mode:
  `partner_cupy_prepared_direct_status_union_component_signature_3d`;
- current route:
  `optix_rt_core_grouped_stream_numba_column_signature_3d`.

Both use `repeat=4`, `warmup=1`, 65,536 points, and the same deterministic datasets.

## Pod Evidence

Artifact:

`docs/reports/goal4114_prepared_direct_status_app_repeat_route_timing_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `0f83ffab`
- Tracked worktree dirty: `false`
- Point count: 65,536
- Repeat: 4
- Warmup: 1

## Result

| Profile | Prepared replay (s) | Current replay (s) | Replay speedup | Prepared amortized (s) | Current amortized (s) | Amortized speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.053269 | 0.095693 | 1.796x | 0.221065 | 0.397566 | 1.798x |
| road3d | 0.027920 | 0.040167 | 1.439x | 0.043068 | 0.081360 | 1.889x |
| ngsim_dense | 0.084930 | 0.015102 | 0.178x | 0.100127 | 0.079571 | 0.795x |

All rows produced matching component-size signatures.

## Interpretation

Prepared direct-status is not a universal RT-DBSCAN replacement.

It is a strong explicit route for the clustered and road profiles in this repeated component-signature contract. It is not the right route for `ngsim_dense`, where the current grouped-stream plus Numba replay path is much faster.

The current route registry should therefore split guidance by shape/reuse evidence rather than promote `partition_convergence_hybrid` globally:

- clustered/road-like repeated component signatures: prepared direct-status is a strong candidate;
- dense NGSIM-like repeated component signatures: current grouped-stream plus Numba remains preferred;
- one-shot app calls: current route remains conservative because prepare cost still matters.

## Boundary

This report does not promote `partition_convergence_hybrid` as a universal default route. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.
