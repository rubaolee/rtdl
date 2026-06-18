# RTDL Backend Maturity

Status: v3.0 source-tree backend maturity guide.

This page separates three claims that are easy to mix up:

- implemented: the backend exists and can be called through RTDL.
- correctness-validated: tests show parity with the reference contract for a
  supported workload.
- performance-ready: the measured path is clean enough to support a bounded
  performance statement.

RTDL should not describe every implemented backend as performance-ready.

For selectable feature behavior, read
[Engine Feature Support Contract](features/engine_support_matrix.md). The
machine-readable feature source is `rtdsl.engine_feature_support_matrix()`.

## Current Summary

| Backend | v2.x release position | Public claim boundary |
| --- | --- | --- |
| CPU reference | Correctness oracle | Useful for parity and debugging, not a speed backend. |
| Embree | Mature CPU RT backend | The default CPU acceleration baseline for all-thread local testing. |
| OptiX | Primary NVIDIA RT backend | Supports RT-core-facing evidence only for reviewed bounded paths on RTX hardware. |
| Vulkan | Proof/portability backend | Preserved support surface; not the main current performance target. |
| HIPRT | Proof backend | Preserved support surface; no AMD performance claim without AMD evidence. |
| Apple RT | Proof/native-assisted backend | Preserved support surface; not a current release performance target. |
| NumPy partner | CPU/reference continuation | Useful for portable examples and correctness checks. |
| CuPy partner | Current measured CUDA continuation performance lane | Recommended for the measured large-scale grouped-reduction and compact-mask custom continuations when performance is the priority. |
| Numba partner | Current no-RawKernel custom-continuation lane | Recommended when users need Python-source custom CUDA-style continuation rows; never auto-selected. |

## How To Read This

Embree and OptiX are the active release-performance engines. Embree gives the
CPU all-thread baseline and OptiX gives the NVIDIA RT path. The other engines
remain valuable for portability, proof coverage, and future work, but current
release-facing performance tables should not lean on them.

The partner layer is separate from the engine ABI. RTDL owns traversal,
candidate discovery, compact rows, bounded witness pages, and app-agnostic
runtime contracts. NumPy, CuPy, Numba, or user code own tensor-side filtering,
reductions, ranking, grouping, or user-authored GPU code when the app needs work
after RTDL returns candidates or witnesses.

## Claim Rules

- `--backend optix` alone is not a speedup claim.
- RT-core wording requires a measured OptiX traversal path on RTX hardware.
- Whole-app speedup wording requires whole-app same-contract evidence.
- Zero-copy wording requires measured device-resident handoff evidence.
- CuPy RawKernel usage is allowed in v2.x app code, but it is partner-side user
  code, not a new app-customized RTDL engine primitive.
- Stale local backend libraries may reject current symbols until rebuilt from
  the current source tree.

## Recommended Backend Choice

| User need | Start here | Reason |
| --- | --- | --- |
| Learn the language | CPU reference, then Embree | Easy setup and deterministic parity. |
| CPU performance | Embree | Mature CPU BVH path with all-thread testing. |
| NVIDIA RT experiments | OptiX | Primary RT-core-facing backend. |
| CUDA-array continuation | CuPy partner | Mature CUDA-array/library continuation and RawKernel-friendly user path. |
| Custom CUDA-style continuation | Numba partner | Current lane for selected measured custom compact-mask and grouped-reduction rows when Python-source no-RawKernel code matters. |
| Portability research | Vulkan, HIPRT, Apple RT | Preserved proof paths with bounded claims. |

## Evidence Links

- [Current Support Matrix](current_main_support_matrix.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Performance Model](performance_model.md)
