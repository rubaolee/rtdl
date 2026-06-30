# Goal4127 - Current Route Decision After 262k Direct-Status Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4127 refreshes the RT-DBSCAN current route decision after the 262k Goal4126 probe.

The change is advisory only: it extends the explicit route-choice evidence table used by `explain_rt_dbscan_explicit_route_choice(...)` and the benchmark-route registry. It does not select a route for the user.

## Route Decision

RT-DBSCAN remains a mixed explicit route:

- one-shot/default: RTDL/OptiX grouped stream plus Numba component-signature continuation;
- repeated component-signature: explicit CuPy prepared direct-status route;
- factor choice: explicit and scale-aware, not automatic.

Current tested guidance:

| Profile family | 65k evidence | 131k evidence | 262k evidence |
| --- | --- | --- | --- |
| clustered/road-like | factor `0.25` | factor `0.25` | factor `0.25` |
| dense NGSIM-like | factor `0.5` | factor `0.25` | factor `0.25` |

The 262k packet makes the route decision more useful for larger repeated workloads: the direct-status route wins all three tested profiles, with `3.118x`, `1.428x`, and `1.642x` replay speedups over the grouped-stream Numba route.

## Boundary

This report does not authorize automatic factor selection, hidden dispatch, automatic partner selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
