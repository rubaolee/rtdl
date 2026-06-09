# Goal4106 - Current RT-DBSCAN Route After Direct Status Comparison

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4106 refreshes the living benchmark route registry after Goal4104 and Goal4105.

Goal4104 showed that direct device status consumption is faster than materializing unordered partition-pair rows when both paths are already inside the resident partition-convergence runtime shape. Goal4105 then asked the stricter route question: if the direct-status preview is called as a naive app-level route, does it beat the current recommended RTDL/OptiX grouped-stream plus Numba route?

The answer is no.

## Registry Update

The route registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4106.v1`

For `rt_dbscan`, the current route remains:

`RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation`

The `partition_convergence_hybrid` family remains explicit and unpromoted.

## Evidence Incorporated

Goal4104 direct status versus materialized unordered partition-pair rows:

| Profile | Direct-status resident speedup |
| --- | ---: |
| clustered3d | 1.239x |
| road3d | 1.508x |
| ngsim_dense | 1.311x |

Goal4105 direct-status app-level route versus current route:

| Profile | Current/direct ratio | Route conclusion |
| --- | ---: | --- |
| clustered3d | 0.475x | direct-status app-level route loses |
| road3d | 0.380x | direct-status app-level route loses |
| ngsim_dense | 0.206x | direct-status app-level route loses |

Goal4104 therefore proves the primitive direction. Goal4105 proves the naive app-level route is not route-promotable while it rebuilds point rows and partition columns every call.

## Design Decision

The next engineering target is not another row-stream micro-cleanup. The next target is a prepared/resident direct-status fixed-radius grouped-union handle:

- prepare point columns, partition keys, offsets, and partition AABBs once;
- consume direct device status without materializing near-pair rows;
- produce component signatures through a generic grouped-union continuation;
- compare against the current RTDL/OptiX grouped-stream plus Numba route only after setup and packing work are no longer repeated.

## Boundary

This report is advisory route metadata only. Users still choose partners explicitly. It does not promote `partition_convergence_hybrid`, does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, native ABI additions, or app-specific native-engine logic.
