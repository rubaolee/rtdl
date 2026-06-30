# RTDL v0.2 Release Statement

Date: 2026-04-07
Status: released as `v0.2.0`

## Statement

RTDL v0.2 is now a released bounded package for non-graphical ray-tracing
workloads.

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

- equal maturity across every backend/workload combination
- full polygon overlay materialization
- generic continuous polygon Jaccard
- native Embree/OptiX/Vulkan Jaccard kernels
- that macOS is a whole-platform closure host

## Platform Interpretation

- Linux is the primary v0.2 validation platform
- macOS is a limited local platform for Python reference, native CPU/oracle
  where available, Embree-oriented work, documentation, and focused local tests

## Relationship To The Newer v0.3 Demo Line

The newer `v0.3` work in this repo should not be read as changing the released
`v0.2.0` package definition.

- `v0.2.0` remains the stable released workload/package surface
- the `v0.3` line is a newer application/demo proof built on the same RTDL core
- the `v0.3` visual-demo work is evidence of versatility, not a replacement release

## External Evidence Note

An Antigravity external test report is preserved as supplementary evidence:

- [Antigravity intake note](../../reports/antigravity_external_review_intake_2026-04-07.md)

It should be read as additional CPU/Embree/PostGIS-oriented evidence, not as
the canonical definition of the released v0.2 surface.
