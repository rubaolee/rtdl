# Goal4118 - Current Route Decision After Tuned Direct-Status Sweep

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4118 refreshes the central benchmark route registry after Goal4116 and Goal4117.

Goal4115 said prepared direct-status was shape-dependent and not universal because `ngsim_dense` lost at the default `partition_cell_factor=0.125`. Goal4116 exposed the partition cell factor as an explicit user-selected app parameter. Goal4117 then showed that explicit tested factors repair the dense-profile regression.

## Route Decision

The `rt_dbscan` row is now a mixed explicit route:

- conservative one-shot/default route: RTDL/OptiX grouped stream plus Numba component-signature continuation;
- repeated component-signature route: explicit CuPy prepared direct-status mode with user-selected `partition_cell_factor`;
- tested factors: `0.25` for clustered/road-like profiles and `0.5` for dense NGSIM-like profiles.

This is not automatic dispatch and not automatic tuning. The user still chooses the route and factor.

## Evidence

Goal4117 measured 65,536-point repeated route timing on RTX 4000 Ada:

| Profile | Factor | Replay Speedup vs Current | Amortized Speedup vs Current |
| --- | ---: | ---: | ---: |
| clustered3d | 0.25 | 2.961x | 9.284x |
| road3d | 0.25 | 1.866x | 2.389x |
| ngsim_dense | 0.5 | 1.312x | 2.484x |

All tested factors matched the current route's component-size signature.

## Next Runtime Action

The next useful work is a user-visible profile/reuse advisor that explains the explicit choices without selecting them automatically. It should answer:

- Is this one-shot or repeated?
- Does the user want the current default grouped-stream Numba route or the explicit prepared direct-status route?
- If using direct-status, which tested `partition_cell_factor` should the user choose and why?

After that, the next performance target is either one-shot prepare-cost reduction or a larger representative-scale packet.

## Boundary

This report does not promote `partition_convergence_hybrid` as a universal default route. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
