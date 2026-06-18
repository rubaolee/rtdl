# V3.0 Toolchain Support Matrix

Status: current V3 source-tree evidence matrix, not a release support guarantee,
packaged SDK promise, or stable ABI contract.

This page defines how to read the toolchain evidence used by the V3
embeddability track. Exact live observations are captured by the corresponding
Goal4604 report; this document defines the boundaries.

## Current Evidence Classes

| Surface | Current Evidence Role | Boundary |
| --- | --- | --- |
| Python | Required source-tree control plane and test runner. | Python availability does not imply package or wheel support. |
| C compiler, `make`, `pkg-config`, CMake | Required to validate C ABI staging, direct-link, prefix, archive, and external CMake consumer smokes. | These are source-tree build tools, not installer evidence. |
| NVIDIA driver / CUDA runtime | Required for current pod-side OptiX and CUDA partner evidence. | Driver/runtime evidence is pod-specific, not a broad GPU support claim. |
| CuPy | Mature CUDA-array partner lane for current pod evidence. | CuPy availability does not mean RTDL accelerates arbitrary CuPy programs. |
| Numba | Python-source CUDA-style partner lane for selected continuations. | Numba availability does not mean automatic partner selection or broad Numba acceleration. |
| RTDL OptiX / Embree libraries | Optional native runtime evidence for current source-tree checks and benchmarks. | Library presence does not authorize performance claims without benchmark-specific evidence. |
| `nvcc` | Useful when rebuilding CUDA/OptiX components from source. | `nvcc` in `PATH` is not required for already-built source-tree consumer smokes. |

## Required Wording

- Say "observed on this pod" when reporting live toolchain versions.
- Say "source-tree handoff" for the current C ABI stage, prefix stage, and archive
  evidence.
- Do not say stable SDK, package install, wheel, broad CUDA support, broad
  RT-core support, or performance claim based only on this matrix.

## Relationship To Other V3 Docs

- [V3.0 Embeddability Architecture Strategy](v3_0_embeddability_architecture_strategy.md)
  defines why the C ABI and data-interoperability boundary matters.
- [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md) defines the
  source-tree stage, prefix stage, archive, pkg-config, and CMake handoff
  shapes.
- [V3.0 Zero-Copy Interop Contract](v3_0_zero_copy_interop_contract.md) defines
  the future zero-copy/device-buffer requirements that this matrix does not
  authorize by itself.
