# RTDL v0.9.4 Release Statement

RTDL `v0.9.4` is the Apple backend consolidation release after `v0.9.1`.

The release absorbs the untagged internal `v0.9.2` Apple performance candidate
and `v0.9.3` Apple native-coverage milestone into one public boundary. It keeps
the released `v0.9.0` HIPRT backend and the released `v0.9.1` Apple closest-hit
slice, then adds the current `v0.9.4` Apple full-surface dispatch and native /
native-assisted coverage.

The correct public statement is:

> RTDL `v0.9.4` makes all 18 current predicates callable through
> `run_apple_rt` on Apple Silicon macOS with explicit native or native-assisted
> modes. Supported geometry and nearest-neighbor slices use Apple MPS RT.
> Bounded DB and graph slices use Apple Metal compute or Metal-filter-plus-CPU
> native-assisted execution. CPU exact refinement, aggregation, uniqueness, or
> ordering remains disclosed where it is part of the implementation.

This release also reorganizes the two newer native engines so HIPRT and Apple
RT follow the same backend-directory pattern as Embree, OptiX, and Vulkan.
Root native files remain thin build wrappers, while backend implementation
chunks live under `src/native/hiprt/` and `src/native/apple_rt/`.

## What v0.9.4 May Claim

- HIPRT and Apple RT are now two newer RTDL backend families alongside Embree,
  OptiX, and Vulkan.
- `run_apple_rt` has explicit support-matrix entries for all 18 current RTDL
  predicates.
- Apple MPS RT is used for supported geometry and nearest-neighbor slices.
- Apple Metal compute/native-assisted execution is used for bounded DB and
  graph slices.
- The Apple and HIPRT native codebases are organized into backend directories
  instead of large single implementation files.

## What v0.9.4 Must Not Claim

- broad Apple speedup
- Apple backend maturity comparable to Embree
- non-macOS Apple backend support
- Apple ray-tracing-hardware traversal for current DB or graph workloads
- AMD GPU validation for HIPRT
- HIPRT CPU fallback
- a broad RT-core speedup claim from GTX 1070 evidence

The release remains a bounded backend/runtime release, not a new DBMS,
renderer, ANN system, graph database, or general-purpose application framework.

