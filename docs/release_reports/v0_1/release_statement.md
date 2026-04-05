# RTDL v0.1 Release Statement

Date: 2026-04-05
Status: released

## Statement

RTDL v0.1 is now released as a bounded, reviewed research-system package for
non-graphical ray-tracing workloads.

This release shows that RTDL can:

- express a real RayJoin-style workload family
- run that workload across multiple serious backends
- preserve explicit correctness boundaries through internal oracles and
  PostGIS comparison
- make performance claims with clear timing-boundary separation

## What the release stands on

The v0.1 trust anchor remains the bounded package documented through the
accepted release matrix and support reports.

The strongest current backend-performance story is the long exact-source
`county_zipcode` positive-hit `pip` surface:

- Embree is parity-clean and faster than PostGIS on the published prepared and
  repeated raw-input boundaries
- OptiX is parity-clean and faster than PostGIS on the same published
  boundaries
- Vulkan is parity-clean and hardware-validated there, but slower

## What the release does not claim

RTDL v0.1 does not claim:

- full paper-identical reproduction of every RayJoin dataset family
- exact computational geometry everywhere
- full polygon overlay materialization
- equal maturity across all backends or workload families

## Canonical release references

- [v0.1 Release Notes](../../v0_1_release_notes.md)
- [v0.1 Reproduction And Verification](../../v0_1_reproduction_and_verification.md)
- [Goal 100 Release Validation Rerun](../../reports/goal100_release_validation_rerun_2026-04-05.md)
- [Goal 102 Full Honest RayJoin Reproduction](../../reports/goal102_full_honest_rayjoin_reproduction_2026-04-05.md)
- [Goal 103 Full Honest RayJoin Reproduction Vulkan](../../reports/goal103_full_honest_rayjoin_reproduction_vulkan_2026-04-05.md)
- [Goal 104 RayJoin Reproduction Performance Report](../../reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)

## Release interpretation

RTDL v0.1 is a research release, not a finished product release.

Its value is that the language/runtime/backends stack now has a reviewed,
auditable, and reproducible bounded package with real backend evidence rather
than only design intent.
