# Goal4135 - Current Route Decision After 524k Factor-0.25 Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4135 refreshes the RT-DBSCAN current route decision after Goal4134 extends the currently winning `partition_cell_factor=0.25` route to 524k.

## Route Decision

RT-DBSCAN remains a mixed explicit route:

- explicit CuPy prepared direct-status route for tested one-shot and repeated component-signature workloads;
- grouped-stream Numba route as the conservative fallback/reference route;
- partition cell factor selected by the user from scale-aware evidence;
- no hidden dispatch, no automatic partner selection, and no automatic factor selection.

Current tested guidance:

| Profile family | 65k evidence | 131k evidence | 262k evidence | 524k evidence |
| --- | --- | --- | --- | --- |
| clustered/road-like | factor `0.25` | factor `0.25` | factor `0.25` | factor `0.25` |
| dense NGSIM-like repeated replay | factor `0.5` | factor `0.25` | factor `0.25` | factor `0.25` |
| dense NGSIM-like one-shot total | factor `0.25` | factor `0.25` | factor `0.25` | factor `0.25` |

The 524k packet does not run a full factor sweep. It only confirms that factor `0.25` remains above parity at the larger scale for the three tested profiles.

The advisor ranks same-scale options by the relevant intent: replay speedup for repeated workloads, and prepare-plus-run total speedup for one-shot workloads. This keeps the 65k dense-profile asymmetry visible instead of flattening it into one universal factor.

## Boundary

This report does not authorize automatic route selection, hidden dispatch, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
