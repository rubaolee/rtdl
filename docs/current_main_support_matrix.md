# RTDL Current Support Matrix

Status: live support matrix for the v2.3 release source tree.

This page is the current learner-facing matrix. Older release matrices remain
under `docs/release_reports/` for audit work, but normal users should read this
page as the single current support view.

For the machine-readable feature-by-engine contract, read
[Engine Feature Support Contract](features/engine_support_matrix.md). Every
public selectable feature must be classified as `native`,
`native_assisted`, `compatibility_fallback`, or `unsupported_explicit`; blank
cells and silent CPU fallback are not allowed.

## Boundary

- Current public docs target: v2.3 release.
- Current released version is `v2.3`.
- Active release engines: Embree for CPU RT, OptiX for NVIDIA RT.
- Active partner direction: v2.5 Triton-first continuation, Numba fallback;
  PyTorch/CuPy remain v2.3 compatibility and conformance surfaces, not the new
  benchmark-path partner direction.
- Engine ABI rule: native backends stay app-agnostic.
- Performance rule: a backend flag is not a speedup claim.
- Release rule: public claims must stay inside the completed external
  consensus gate.

## Engine Support Shape

| Surface | CPU reference | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- | --- |
| Any-hit rows | supported | native | native | native | native | native-assisted |
| Hit counts | supported | native | native | native | native | native-assisted |
| Closest hit | supported | native | native | native | native | native |
| Fixed-radius rows | supported | native | native | native | native | native-assisted |
| KNN rows | supported | native | native | native | native | native-assisted |
| Segment/polygon witnesses | supported | native | native | native | proof path | proof path |
| Bounded polygon summaries | supported | native-assisted | native-assisted | not a release target | not a release target | not a release target |
| DB-style compact summaries | supported | native | native | proof path | proof path | proof path |
| Graph traversal rows | supported | native | native | proof path | proof path | proof path |
| Partner tensor continuation | Python-owned | CPU partner path | Triton-first preview plus legacy PyTorch/CuPy compatibility | not a release target | not a release target | not a release target |

## Current Performance Reading

Use the v2.3 performance tables as app-level evidence, not as a universal
backend ranking. The useful reading is:

- Embree measures the CPU RT path plus CPU partner continuation.
- OptiX measures NVIDIA RT traversal plus GPU partner continuation when the app
  uses one.
- A fast compact summary does not imply full witness-row output is equally
  fast.
- A CuPy RawKernel continuation is allowed as legacy partner/user code and
  should be documented as such. New v2.5 benchmark-path continuation work should
  target Triton first.

## Non-Claims

Do not use this matrix to claim:

- broad speedup across all workloads;
- package-install support;
- AMD GPU performance;
- Apple RT performance for the v2.3 release target;
- that partner-side RawKernel, PyTorch, or NumPy code is part of the native
  app-agnostic RTDL engine;
- true zero-copy unless the exact measured path proves device-resident handoff.

## Where To Go Next

- [Backend Maturity](backend_maturity.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Performance Model](performance_model.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
