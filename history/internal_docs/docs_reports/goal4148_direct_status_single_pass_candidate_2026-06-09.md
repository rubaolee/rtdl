# Goal4148 - Direct-Status Single-Pass Candidate

Date: 2026-06-09

Verdict: implementation-complete-pod-measured-in-goal4149

## Purpose

Goal4147 showed that the 1M RT-DBSCAN prepared direct-status path uses two
union iterations for all tested factor-0.25 profiles. The first pass performs
the useful union work and the second pass proves convergence. Goal4148 exposes
an explicit `single_pass_candidate` mode so the candidate can be measured and
validated without changing the stable default.

## Implementation

The prepared direct-status runtime now accepts:

- `convergence_mode="until_stable"`: the default convergence-proven loop.
- `convergence_mode="single_pass_candidate"`: one direct-status scan plus parent
  compression, marked as a candidate and not promoted.

The benchmark CLI forwards this through
`--direct-status-convergence-mode`. Metadata records the selected mode,
the final `changed` flag, whether convergence was proven, and whether the
single-pass candidate was used.

## Boundary

This is not a route promotion. The default remains `until_stable`; the app
metadata keeps `direct_status_single_pass_promoted` false. Goal4149 compares
component-size signatures against the stable route on the 1M factor-0.25 pod
packet and keeps the result bounded as same-signature evidence, not a universal
convergence proof.

This goal does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, hidden dispatch,
automatic partner selection, automatic partition-cell-factor selection,
app-specific engine logic, native ABI additions, AMD claims, or true-zero-copy
claims.
