# Goal4153 - RT-DBSCAN Current-Route Versus Single-Pass Negative Probe

Date: 2026-06-09

Verdict: reject-as-performance-comparison

## Purpose

Goal4153 attempted to compare the conservative current RT-DBSCAN route
(`optix_rt_core_grouped_stream_numba_column_signature_3d`) directly against the
Goal4151 explicit `single_pass_candidate` direct-status route.

The result is useful, but not as a speedup table: the signatures do not match.

## Artifact

`docs/reports/goal4153_rtdbscan_current_vs_single_pass_factor025_pod.json`

Setup:

- Source commit: `a94f87c6`
- Point counts: 65,536 / 131,072 / 262,144 / 524,288 / 1,048,576
- Repeat: 2
- Warmup: 1
- Factor for single-pass direct-status: `0.25`
- Profiles: `clustered3d`, `road3d`, `ngsim_dense`

## Result

All 15 rows report `same_signature_vs_current = false`. Therefore the timing
ratios in the artifact are not valid same-contract performance comparisons.

The apparent ratios range from `0.230x` to `5.321x`, but those numbers must not
be used as a benchmark claim because they compare different route contracts.

## Interpretation

The valid Goal4149/Goal4150 comparison is:

- stable direct-status convergence loop
- versus explicit single-pass direct-status candidate
- with same component-size signatures on the measured profiles/scales

The invalid Goal4153 comparison is:

- conservative current grouped-stream/Numba route
- versus direct-status component-signature candidate
- with mismatched signatures

Goal4153 therefore becomes a guardrail: do not collapse these rows into a single
"current versus single-pass" speedup table unless a same-contract adapter is
added first.

## Boundary

This goal does not authorize route promotion, release, public speedup wording,
broad RT-core wording, whole-app benchmark claims, paper reproduction, hidden
dispatch, automatic partner selection, automatic partition-cell-factor
selection, automatic convergence-mode selection, app-specific engine logic,
native ABI additions, AMD claims, or true-zero-copy claims.
