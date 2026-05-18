# RTDL Backend Maturity

Status: current v2.0 release backend maturity guide.

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

| Backend | v2.0 pre-release position | Public claim boundary |
| --- | --- | --- |
| CPU reference | Correctness oracle | Useful for parity and debugging, not a speed backend. |
| Embree | Mature CPU RT backend | The default CPU acceleration baseline for all-thread local testing. |
| OptiX | Primary NVIDIA RT backend | Supports RT-core-facing evidence only for reviewed bounded paths on RTX hardware. |
| Vulkan | Proof/portability backend | Preserved support surface; not the main v2.0 performance target. |
| HIPRT | Proof backend | Preserved support surface; no AMD performance claim without AMD evidence. |
| Apple RT | Proof/native-assisted backend | Preserved support surface; not a v2.0 release performance target. |
| PyTorch partner | Reference partner direction | Current v2.0 partner model for tensor-side work where PyTorch can express it. |
| CuPy partner | Conformance and GPU escape-hatch partner | Current v2.0 partner model for device arrays and explicit user kernels where needed. |

## How To Read This

Embree and OptiX are the active release-performance engines. Embree gives the
CPU all-thread baseline and OptiX gives the NVIDIA RT path. The other engines
remain valuable for portability, proof coverage, and future work, but v2.0
release-facing performance tables should not lean on them.

The partner layer is separate from the engine ABI. RTDL owns traversal,
candidate discovery, compact rows, bounded witness pages, and app-agnostic
runtime contracts. PyTorch or CuPy own tensor-side filtering, reductions,
ranking, grouping, or user-authored GPU code when the app needs work after RTDL
returns candidates or witnesses.

## Claim Rules

- `--backend optix` alone is not a speedup claim.
- RT-core wording requires a measured OptiX traversal path on RTX hardware.
- Whole-app speedup wording requires whole-app same-contract evidence.
- True zero-copy wording requires measured device-resident handoff evidence.
- CuPy RawKernel usage is allowed in v2.0 app code, but it is partner-side user
  code, not a new app-customized RTDL engine primitive.
- Stale local backend libraries may reject current symbols until rebuilt from
  the current source tree.

## Recommended Backend Choice

| User need | Start here | Reason |
| --- | --- | --- |
| Learn the language | CPU reference, then Embree | Easy setup and deterministic parity. |
| CPU performance | Embree | Mature CPU BVH path with all-thread testing. |
| NVIDIA RT experiments | OptiX | Primary RT-core-facing backend. |
| Tensor continuation | PyTorch or CuPy partner | Keeps non-RT work outside the app-agnostic engine. |
| Portability research | Vulkan, HIPRT, Apple RT | Preserved proof paths with bounded claims. |

## Evidence Links

- [Current Support Matrix](current_main_support_matrix.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Performance Model](performance_model.md)
- [v2.0 Release Package](release_reports/v2_0/README.md)
