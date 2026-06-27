# Codex Consensus: Goal 148 v0.2 Scope Decision

Claude, Gemini, and Codex agree on the main decision:

- v0.2 should stop feature growth at exactly these four live workload surfaces:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness and performance evidence
- explicit fallback-vs-native backend honesty boundaries

Agreed exclusions:

- no new workload families before release-shaping
- no full polygon overlay/materialization
- no generic continuous polygon Jaccard
- no raw freehand pathology Jaccard closure
- no native Jaccard backend-maturity claims
- no broad generate-only expansion

Agreed next steps:

1. one canonical v0.2 scope/status package
2. one front-door and example consistency freeze
3. one release-readiness/stability pass
