# RTDL v0.2 Scope And Status

Date: 2026-04-07
Status: accepted scope freeze for release-shaping

## Conclusion

RTDL v0.2 should now stop feature growth and move into release-shaping.

The accepted live v0.2 scope is:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness and performance evidence
- explicit fallback-vs-native backend honesty boundaries

## Why This Is Enough

v0.2 has already proved the key release-defining point:

- RTDL is broader than the archived v0.1 RayJoin-heavy slice
- it now has multiple real workload families, not only one bounded trust-anchor
  story
- those families have tests, examples, docs, and Linux-backed evidence

So the highest-value next work is no longer more feature growth.
It is:

- scope freeze
- consistency
- release-readiness

## Accepted Workload Surface

### 1. `segment_polygon_hitcount`

Accepted as:

- a real closed segment/polygon counting workload family
- Linux/PostGIS-backed
- strong on the accepted large deterministic Linux rows

### 2. `segment_polygon_anyhit_rows`

Accepted as:

- a real closed segment/polygon join-row workload family
- Linux/PostGIS-backed
- strong on the accepted large deterministic Linux rows

### 3. `polygon_pair_overlap_area_rows`

Accepted as:

- the narrow primitive for the Jaccard line
- under the orthogonal integer-grid unit-cell contract
- not full generic polygon overlay

### 4. `polygon_set_jaccard`

Accepted as:

- the narrow aggregate Jaccard workload
- under the same unit-cell pathology-style contract
- not generic continuous polygon-set Jaccard

## Supporting Surface Included In v0.2

### Generate-only

Accepted in narrow form only:

- current accepted segment/polygon workloads
- one authored `polygon_set_jaccard` entry

Not accepted as:

- broad general code generation

### Feature-home docs

Accepted as a core part of the language surface:

- one canonical feature directory per supported workload
- purpose, code, example, best practices, try/try-not, limitations

### Linux evidence

Accepted as the primary validation story for:

- PostGIS-backed correctness
- large-scale runtime evidence
- OptiX
- Vulkan

## Platform Boundary

### Primary platform

Linux is the primary v0.2 development and validation platform.

Use Linux for:

- PostGIS-backed correctness
- large deterministic and stress performance runs
- OptiX
- Vulkan
- final whole-system validation

### Limited local platform

This Mac is a limited local platform.

Use it for:

- Python reference
- native CPU/oracle where available
- Embree-oriented local work
- docs
- focused local tests

Do not treat this Mac as the primary closure platform for:

- OptiX
- Vulkan
- Linux/PostGIS evidence
- final whole-system release closure

## Backend Honesty Boundary

### Segment/polygon line

For the two segment/polygon families:

- Linux large-row evidence is strong across:
  - CPU
  - Embree
  - OptiX
  - Vulkan

But this still does not imply:

- universal RT-core-native maturity for every future workload

### Jaccard line

For the Jaccard workloads:

- Python and native CPU are the strongest current implementation story
- PostGIS remains the external correctness anchor on accepted packages
- the public `embree`, `optix`, and `vulkan` run surfaces are accepted on
  Linux through documented native CPU/oracle fallback

This does **not** mean:

- native Embree Jaccard kernels
- native OptiX Jaccard kernels
- native Vulkan Jaccard kernels
- RT-core maturity for the Jaccard line

## Explicitly Out Of Scope For v0.2

Do not add these before release-shaping:

- new workload families
- full polygon overlay/materialization
- generic continuous polygon Jaccard
- raw freehand pathology Jaccard closure
- native Jaccard backend-maturity claims
- broad generate-only expansion
- AMD/Intel backend work

## Next Release-Shaping Goals

### Goal 149

Front-door and example consistency freeze:

- README
- docs index
- user guide
- cookbook
- examples
- release-facing wording

### Goal 150

Release-readiness and stability pass:

- rerun accepted current surfaces
- confirm support matrix
- confirm docs/code/example consistency
- publish final readiness statement

## Review Closure

This scope decision is supported by:

- [Claude scope review](/Users/rl2025/rtdl_python_only/docs/reports/goal148_scope_decision_claude_2026-04-07.md)
- [Gemini scope review](/Users/rl2025/rtdl_python_only/docs/reports/goal148_scope_decision_gemini_2026-04-07.md)
- [Codex consensus](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-07-codex-consensus-goal148-v0_2-scope-decision.md)
