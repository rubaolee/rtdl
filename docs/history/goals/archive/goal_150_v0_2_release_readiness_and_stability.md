# Goal 150: v0.2 Release Readiness And Stability

## Why

v0.2 scope is now frozen. Before a final release package can be shaped, the
repo needs one narrow readiness pass that checks the accepted v0.2 surface as
it actually exists on current `main`.

This goal is not another feature goal.

It is a release-shaping goal that checks:

- frozen v0.2 test stability
- release-facing example stability
- feature-home and front-door doc consistency
- the Linux-primary / Mac-limited platform split
- the fallback-vs-native honesty boundary for the Jaccard line

## Scope

Produce one checked-in release-readiness package for the frozen v0.2 scope:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- the release-facing example layer

## Acceptance

- a checked-in release-readiness report exists
- it uses current `main`, not stale historical state
- it includes:
  - local Mac `v0_2_local` status
  - fresh Linux `v0_2_full` status from a clean checkout
  - fresh release-facing example smoke results
  - feature-home and release-surface audit results
  - a fresh several-second Linux Jaccard consistency row
- it states clearly what is accepted and what is still environment-bounded
- it has `2+` review coverage with at least one Claude or Gemini review before
  online closure
