# Goal4110 - Current RT-DBSCAN Route After Prepared Direct Status App Mode

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4110 refreshes the living benchmark route registry after Goal4108 and Goal4109.

The key distinction is now precise:

- one-shot default route: keep RTDL/OptiX grouped stream plus Numba component/signature continuation;
- repeated component-signature route: users may explicitly choose the CuPy prepared direct-status union app mode when they reuse the same point/partition columns.

There is still no hidden dispatch or automatic partner choice.

## Registry Update

The route registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4110.v1`

For `rt_dbscan`, the current route remains:

`RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation`

The new explicit app mode is:

`partner_cupy_prepared_direct_status_union_component_signature_3d`

## Evidence Incorporated

Goal4108 prepared replay evidence:

| Profile | Replay vs one-shot direct | Replay vs current route |
| --- | ---: | ---: |
| clustered3d | 1.802x | 3.752x |
| road3d | 2.465x | 4.648x |
| ngsim_dense | 1.488x | 1.207x |

Goal4109 app-mode smoke:

| Dataset | Point count | Elapsed (s) | Prepare (s) | Signature (s) | Boundary |
| --- | ---: | ---: | ---: | ---: | --- |
| tiny | 9 | 0.531371 | 0.446152 | 0.067556 | validates |
| clustered3d | 65,536 | 0.560136 | 0.503871 | 0.056235 | one-shot smoke |

## Decision

Prepared direct-status replay is now a real explicit route for repeated component-signature workloads. It should not be promoted as the universal one-shot default yet, because the app-mode smoke remains prepare-dominated and `ngsim_dense` has a narrower replay margin than the other two profiles.

The next engineering target is a route-level repeated prepared direct-status app packet and an explicit reuse threshold. If that packet remains positive, RT-DBSCAN guidance can split one-shot and repeated-use recommendations more strongly.

## Boundary

This report is advisory route metadata only. Users still choose partners explicitly. It does not promote `partition_convergence_hybrid`, does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, native ABI additions, or app-specific native-engine logic.
