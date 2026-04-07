# Codex Consensus: Goal 151 Front-Door Status Freeze

## Verdict

Accepted.

## Why

Goal 151 does the right final front-door work for the frozen v0.2 stage:

- it makes the accepted four-workload v0.2 scope explicit
- it repeats the Linux-primary / Mac-limited split consistently
- it repeats the Jaccard fallback-vs-native boundary consistently
- it keeps the release-facing docs aligned with Goals 148, 149, and 150

## Agreed Boundaries

- frozen v0.2 scope:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- Linux is the primary validation platform
- this Mac is a limited local platform
- the Jaccard line remains fallback-bounded on the public Embree/OptiX/Vulkan
  run surfaces
- this goal is wording freeze, not final release tagging
