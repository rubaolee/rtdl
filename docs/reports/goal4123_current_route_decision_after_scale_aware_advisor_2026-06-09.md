# Goal4123 - Current Route Decision After Scale-Aware RT-DBSCAN Advisor

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4123 refreshes the route registry after the 131k Goal4122 scale probe.

Goal4118 correctly recorded the 65k tuned direct-status win, but it was too simple for dense NGSIM-like profiles: Goal4117 found factor `0.5` best at 65k, while Goal4122 found factor `0.25` best at 131k.

## Route Decision

RT-DBSCAN remains a mixed explicit route:

- one-shot/default: RTDL/OptiX grouped stream plus Numba component-signature continuation;
- repeated component-signature: explicit CuPy prepared direct-status route;
- factor choice: explicit and scale-aware, not automatic.

Current tested guidance:

| Profile family | 65k evidence | 131k evidence |
| --- | --- | --- |
| clustered/road-like | factor `0.25` | factor `0.25` |
| dense NGSIM-like | factor `0.5` | factor `0.25` |

Users should consult the advisory route packet instead of treating any dense-profile factor as universal.

## Boundary

This report does not authorize automatic factor selection, hidden dispatch, automatic partner selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
