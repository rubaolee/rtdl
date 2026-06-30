# RTDL v0.9.2 Release Statement

Public status note: `v0.9.2` was not tagged as a public release. This statement
records an internal Apple RT candidate/evidence line that was later absorbed
into the released `v0.9.4` Apple RT consolidation. For the current public
release boundary, use `../v0_9_5/release_statement.md`.

RTDL `v0.9.2` is the Apple RT usability and performance candidate release.

The release candidate expands the `v0.9.1` Apple RT closest-hit slice in three
ways:

- `run_apple_rt` can now be used as a full-surface entry point for the current
  18 RTDL predicates on Apple Silicon macOS.
- Apple RT native execution is explicit and bounded: 3D closest-hit, 3D
  hit-count, and 2D segment-intersection use Apple Metal/MPS RT; the other
  predicates are compatibility paths through the CPU reference unless
  `native_only=True` is requested.
- Prepared closest-hit reuse and masked chunked traversal reduce overhead for
  repeated Apple RT workloads.

The correct public interpretation is:

> Apple RT is now a more serious RTDL backend path for Apple developers, with
> native slices beyond closest-hit and better repeated-query ergonomics. It is
> not yet a broad speedup release.

Goal600 local Apple M4 evidence:

- 3D closest-hit: Apple RT median `0.001410938s`, Embree median
  `0.002579126s`, parity true, stable
- 3D hit-count: Apple RT median `0.115251041s`, Embree median `0.002449166s`,
  parity true, unstable
- 2D segment-intersection: Apple RT median `0.030149874s`, Embree median
  `0.007471208s`, parity true, stable

Therefore:

- closest-hit can be described as faster than Embree on the current local Apple
  M4 fixture
- hit-count must be described as correct but not performance-ready
- segment-intersection must be described as correct and improved but still
  slower than Embree on the current fixture
- Embree remains the mature RTDL performance baseline

The release keeps all `v0.9.0` HIPRT and closest-hit boundaries intact and all
`v0.9.1` Apple RT closest-hit boundaries intact.
