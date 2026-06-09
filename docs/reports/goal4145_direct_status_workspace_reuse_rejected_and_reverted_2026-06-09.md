# Goal4145 - Direct-Status Workspace Reuse Rejected And Reverted

Date: 2026-06-09

Verdict: accept

## Purpose

Goal4145 closes the Goal4143/Goal4144 workspace-reuse probe by restoring the
active runtime to the faster pre-candidate direct-status path.

## Decision

Goal4144 showed that prepared workspace reuse was not a meaningful performance
win at 1M points:

- replay was neutral (`0.998x`, `1.000x`, `1.001x` versus Goal4138);
- one-shot totals were worse (`0.992x`, `0.995x`, `0.957x`);
- component-size signatures stayed correct.

The active direct-status helper therefore returns to per-run parent/counter
allocation with `cupy.arange`/`cupy.zeros`. This is the measured faster default
for the current implementation.

## Boundary

This goal does not change the user-visible route guidance from Goal4139. It does
not authorize release, public speedup wording, broad RT-core wording, whole-app
benchmark claims, paper reproduction, automatic dispatch, automatic partner
selection, automatic factor selection, app-specific engine logic, native ABI
additions, AMD claims, or true-zero-copy claims.

The next performance target should be structural: direct-status kernel work,
convergence/sync behavior, prepare pipeline cost, or a stronger native/resident
partition producer.
