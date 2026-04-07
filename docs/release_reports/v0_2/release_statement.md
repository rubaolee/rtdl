# RTDL v0.2 Release Statement

Date: 2026-04-07
Status: ready for tag preparation

## Statement

RTDL v0.2 is now a frozen release-shaping package for non-graphical
ray-tracing workloads.

This version expands RTDL beyond the archived v0.1 trust anchor while keeping
explicit platform and backend honesty boundaries.

The accepted v0.2 workload surface is exactly:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness/performance evidence
- explicit fallback-vs-native backend honesty boundaries

## What The Release Stands On

The strongest current v0.2 evidence chain is:

- Linux/PostGIS-backed correctness and large-row evidence for:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- narrow public-data-derived Jaccard closure for:
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- Linux wrapper-surface consistency for the Jaccard line on:
  - `embree`
  - `optix`
  - `vulkan`
  under documented native CPU/oracle fallback
- repaired Linux OptiX SDK-path robustness so `make build-optix` now discovers
  the real accepted host SDK location automatically
- release-facing examples, feature-home docs, and generate-only support for the
  accepted frozen surface

## What The Release Does Not Claim

RTDL v0.2 does not claim:

- final tagged release closure yet
- equal maturity across every backend/workload combination
- full polygon overlay materialization
- generic continuous polygon Jaccard
- native Embree/OptiX/Vulkan Jaccard kernels
- that this Mac is a whole-platform closure host

## Platform Interpretation

- Linux is the primary v0.2 validation platform
- this Mac is a limited local platform for Python reference, native CPU/oracle
  where available, Embree-oriented work, documentation, and focused local tests

## External Evidence Note

An Antigravity external test report is preserved as supplementary evidence:

- [Antigravity intake note](../../reports/antigravity_external_review_intake_2026-04-07.md)

It should be read as additional CPU/Embree/PostGIS-oriented evidence, not as
the canonical definition of the frozen v0.2 release surface.
