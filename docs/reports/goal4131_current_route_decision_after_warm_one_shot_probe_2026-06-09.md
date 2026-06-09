# Goal4131 - Current Route Decision After Warmed One-Shot Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4131 refreshes the RT-DBSCAN current route decision after Goal4130 shows the tuned prepared direct-status route wins not only repeated replay but also warmed one-shot prepare-plus-one-run timing at the tested scales.

## Route Decision

RT-DBSCAN remains a mixed explicit route:

- explicit CuPy prepared direct-status route for tested one-shot and repeated component-signature workloads;
- grouped-stream Numba route as the conservative fallback/reference route;
- partition cell factor selected by the user from scale-aware evidence;
- no hidden dispatch, no automatic partner selection, and no automatic factor selection.

Current tested guidance:

| Profile family | 65k evidence | 131k evidence | 262k evidence |
| --- | --- | --- | --- |
| clustered/road-like | factor `0.25` | factor `0.25` | factor `0.25` |
| dense NGSIM-like | factor `0.5` | factor `0.25` | factor `0.25` |

Goal4130 adds one-shot total evidence, with prepared direct-status beating grouped-stream Numba by `1.819x` to `3.410x` after prepare is charged once for the measured query.

## Boundary

This report does not authorize automatic route selection, hidden dispatch, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
