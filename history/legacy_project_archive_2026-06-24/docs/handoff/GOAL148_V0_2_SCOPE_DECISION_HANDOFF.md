# Goal 148 v0.2 Scope Decision Handoff

Please review this proposed RTDL v0.2 scope decision.

## Proposed decision

Freeze v0.2 feature growth at exactly these four live workload surfaces:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness and performance evidence
- explicit fallback-vs-native backend honesty boundaries

Do **not** add new workload families before release-shaping.

## What should not be in v0.2

- new workload families
- full polygon overlay/materialization
- generic continuous polygon Jaccard
- raw freehand pathology Jaccard closure
- native Jaccard RT-core/backend maturity claims
- broad generate-only expansion
- AMD/Intel backend work

## Proposed next goals

1. one canonical v0.2 scope/status package
2. one front-door and example consistency freeze
3. one release-readiness/stability pass

## Review ask

Evaluate whether this is the right and honest v0.2 stopping scope.

Return exactly three short sections titled:

- `Verdict`
- `Findings`
- `Summary`
