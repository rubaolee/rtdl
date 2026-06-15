# RTDL Current Support Matrix

Status: live support matrix for the v2.14 source tree.

This page is the current learner-facing matrix. Older release matrices remain
under `docs/release_reports/` for audit work, but normal users should read this
page as the single current support view.

For the machine-readable feature-by-engine contract, read
[Engine Feature Support Contract](features/engine_support_matrix.md). Every
public selectable feature must be classified as `native`,
`native_assisted`, `compatibility_fallback`, or `unsupported_explicit`; blank
cells and silent CPU fallback are not allowed.

## Boundary

- Current docs target: v2.14 source-tree partner-choice guidance.
- Active release engines: Embree for CPU RT, OptiX for NVIDIA RT.
- Active v2.14 direction: primitive-first native RTDL when a fused generic
  primitive exactly expresses the work; explicit partner continuation only for
  unfused work or app choice; users choose supported partners explicitly, while
  benchmark recommendations must be backed by same-contract evidence, stated
  directionally, and never by hidden defaults.
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
| Partner tensor/custom continuation | Python-owned | CPU partner path | explicit user/app-chosen partner path for unfused continuations; CuPy is the mature CUDA-array lane, and Numba is the current Python-source custom-kernel lane | not a release target | not a release target | not a release target |

## Current Performance Reading

Use the current performance tables as app-level evidence, not as a universal
backend ranking. The useful reading is:

- Embree measures the CPU RT path plus CPU partner continuation.
- OptiX measures NVIDIA RT traversal plus GPU partner continuation when the app
  uses one.
- A fast compact summary does not imply full witness-row output is equally
  fast.
- A CuPy RawKernel or Numba CUDA continuation is allowed as partner/user code
  and should be documented as such. New continuation work should first ask
  whether a fused native RTDL primitive already expresses the continuation; if
  not, the partner is an explicit user/app choice. Benchmark reference
  implementations can recommend a partner only when same-contract evidence
  supports that path.

## Non-Claims

Do not use this matrix to claim:

- broad speedup across all workloads;
- package-install support;
- AMD GPU performance;
- Apple RT performance for the current release target;
- that partner-side RawKernel, Numba, or NumPy code is part of the native
  app-agnostic RTDL engine;
- zero-copy unless the exact measured path proves device-resident handoff.

## Where To Go Next

- [Backend Maturity](backend_maturity.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Performance Model](performance_model.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
