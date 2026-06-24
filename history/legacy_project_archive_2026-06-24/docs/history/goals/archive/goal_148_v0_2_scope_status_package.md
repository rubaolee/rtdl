# Goal 148: v0.2 Scope/Status Package

## Why

v0.2 now has enough real feature work to stop growing and start shaping a
release. The project needs one canonical package that states:

- what v0.2 includes
- what v0.2 explicitly does not include
- which backend/platform boundaries are accepted
- what the next release-shaping steps are

## Scope

Produce one canonical v0.2 scope/status statement that freezes the accepted
live v0.2 surface at:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness/performance evidence
- explicit fallback-vs-native backend honesty boundaries

## Not In Scope

- new workload families
- full polygon overlay/materialization
- generic continuous polygon Jaccard
- raw freehand pathology Jaccard closure
- native Jaccard backend-maturity claims
- broad generate-only expansion
- AMD/Intel backend work

## Acceptance

- one canonical checked-in v0.2 scope/status report exists
- it states in-scope surfaces and out-of-scope exclusions clearly
- it makes the Linux-primary / Mac-limited platform split explicit
- it states the fallback-vs-native Jaccard boundary explicitly
- it records the agreed next release-shaping goals
- it has `2+` review coverage with at least one Claude or Gemini review
