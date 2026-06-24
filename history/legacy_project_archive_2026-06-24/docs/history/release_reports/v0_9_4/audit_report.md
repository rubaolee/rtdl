# RTDL v0.9.4 Audit Report

Date: 2026-04-19

Status: released audit package.

## Audit Scope

This audit checks the `v0.9.4` release for:

- total test evidence
- public documentation consistency
- backend/platform honesty
- Apple RT support-matrix accuracy
- HIPRT/Apple code-organization stability
- flow integrity after absorbing the internal `v0.9.2` and `v0.9.3` evidence
  lines

## Release Boundary

`v0.9.4` is the public consolidation of post-`v0.9.1` Apple backend work:

- internal `v0.9.2`: Apple RT full-surface dispatch, prepared closest-hit reuse,
  and early Apple performance/overhead evidence
- internal `v0.9.3`: expanded Apple MPS RT geometry and nearest-neighbor
  native/native-assisted coverage
- public `v0.9.4`: Apple Metal compute/native-assisted DB and graph coverage,
  explicit Apple support matrix for all 18 current predicates, and HIPRT/Apple
  backend code reorganization

The released `v0.9.0` HIPRT surface remains part of the current project state.
The released `v0.9.1` Apple closest-hit slice is superseded by the `v0.9.4`
Apple consolidation release.

## Documentation Audit

Public docs now state:

- current released version is `v0.9.4`
- `v0.9.2` and `v0.9.3` remain internal evidence lines, not public releases
- `v0.9.2` and `v0.9.3` were internal evidence lines, not public releases
- HIPRT and Apple RT are newer backend families
- Apple DB and graph paths are Metal compute/native-assisted paths, not Apple
  ray-tracing-hardware traversal paths
- Embree remains the only backend called optimized/mature
- Apple RT is correctness-validated for bounded native/native-assisted slices
  but is not a broad performance-leading claim

## Code Organization Audit

Goal624 split the two newer native backend files:

- Apple: `src/native/rtdl_apple_rt.mm` is now a thin wrapper over
  `src/native/apple_rt/`
- HIPRT: `src/native/rtdl_hiprt.cpp` is now a thin wrapper over
  `src/native/hiprt/`

This mirrors the existing Embree, OptiX, and Vulkan directory layout. Build
entry points and exported C ABI names remain unchanged.

## Test Evidence

Evidence to be recorded in the final gate report:

- local full unittest discovery
- local Apple backend build and focused Apple suite
- Linux HIPRT build and focused HIPRT suite
- public documentation smoke/link tests
- public entry smoke
- public command truth audit
- final whitespace/status checks

## Known Non-Claims

This audit rejects the following claims:

- Apple DB or graph workloads are accelerated by Apple ray-tracing hardware.
- Apple RT is broadly faster than Embree.
- HIPRT is AMD-GPU validated.
- HIPRT has a CPU fallback.
- `v0.9.2` or `v0.9.3` were public releases.
- RTDL is a DBMS, graph database, renderer, ANN system, or general app
  framework.

## Audit Verdict

No release-blocking documentation or flow inconsistency is known after the
Goal623, Goal624, and Goal625 corrections and reviews.
