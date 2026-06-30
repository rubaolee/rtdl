# Goal4115 - Current Route Decision After Shape-Dependent Direct Status Evidence

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4115 refreshes the central benchmark route registry after Goal4114's route-level repeated RT-DBSCAN packet.

The key update is that prepared direct-status is useful, but not universal:

- clustered/road-like repeated component-signature workloads: explicit CuPy prepared direct-status wins;
- dense NGSIM-like repeated component-signature workloads: the current RTDL/OptiX grouped-stream plus Numba route remains faster;
- one-shot calls: the current route remains the conservative default because prepare cost still matters.

## Evidence

Goal4114 measured `repeat=4`, `warmup=1`, 65,536 points on RTX 4000 Ada:

| Profile | Prepared replay (s) | Current replay (s) | Replay speedup | Prepared amortized (s) | Current amortized (s) | Amortized speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.053269 | 0.095693 | 1.796x | 0.221065 | 0.397566 | 1.798x |
| road3d | 0.027920 | 0.040167 | 1.439x | 0.043068 | 0.081360 | 1.889x |
| ngsim_dense | 0.084930 | 0.015102 | 0.178x | 0.100127 | 0.079571 | 0.795x |

All rows produced matching component-size signatures.

## Route Registry Change

`CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4115.v1`

The `rt_dbscan` row now says:

- current one-shot route remains `RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation`;
- users may explicitly choose `partner_cupy_prepared_direct_status_union_component_signature_3d` for clustered/road-like repeated component-signature workloads;
- users should keep grouped-stream Numba for dense NGSIM-like repeated component signatures unless new same-contract evidence beats it;
- universal `partition_convergence_hybrid` promotion remains rejected after Goal4114.

## Next Runtime Action

The next serious work is no longer "measure repeated app timing"; Goal4114 did that. The remaining choices are:

1. Add a user-visible, advisory profile/reuse explanation that helps users choose between grouped-stream Numba and prepared direct-status without hidden dispatch.
2. Build a new dense-profile direct-status improvement that removes the `ngsim_dense` regression.

Either route must remain explicit user choice. No automatic partner selection or hidden dispatch is authorized.

## Boundary

This report does not promote `partition_convergence_hybrid` as a universal default route. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
