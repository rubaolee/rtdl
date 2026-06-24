# Goal 2025 Proposal: Triton and Numba "User-Select-Partner" Backends

**Date**: 2026-05-14
**Author**: Gemini/Antigravity (User Proposal)
**Status**: proposed-for-review

## 1. Problem Statement: The Limits of CuPy RawKernel

RTDL v2.0 successfully established a clean architectural boundary: the native engine (OptiX/Embree) emits purely generic geometric candidate pairs, while the "Partner Layer" (PyTorch/CuPy) handles domain-specific continuation and exact filtering on the GPU. 

This zero-copy architecture yields massive performance gains. However, when standard tensor reductions (e.g., `cupy.bincount`, `cupy.scatter_add`) are not expressive enough to capture complex app semantics, developers are forced to use **CuPy RawKernel**. 

While highly performant, `RawKernel` requires writing C++/CUDA code inside Python strings. This breaks the ultimate promise of RTDL v2.0: enabling data scientists and Python developers to build high-performance ray-tracing applications without touching C++.

## 2. Proposed Solution: Triton and Numba Integration

We propose expanding the partner layer into a modular **"User-Select-Partner" mode**, officially introducing **Triton** and **Numba** as first-class partner backends alongside PyTorch and CuPy.

### The Mechanism
1. **Unchanged Native Engine**: The OptiX/Embree native engines continue to output generic `generic_ray_primitive_candidate_witness_pairs` as device pointers.
2. **Pure Python Custom Primitives**: Instead of routing these pointers to a CuPy RawKernel, RTDL routes them to a user-defined Triton or Numba kernel.
3. **Familiar Syntax**: Users write their highly specific domain logic (e.g., custom acoustic wave attenuation, complex exact polygon intersections) using pure Python syntax annotated with `@triton.jit` or `@numba.cuda.jit`.

## 3. Architectural Benefits

* **100% Python Experience**: Users can write custom, highly specialized GPU operators without leaving the Python syntax ecosystem. 
* **Preserved Zero-Copy Boundary**: Triton and Numba can directly accept the raw device pointers (or CuPy/Torch tensors wrapping them) emitted by the native engine, maintaining the strict zero-copy mandate of v2.0.
* **Ultimate Extensibility**: This officially transforms RTDL from just a "library of pre-built operators" into an extensible framework where users can safely and easily inject their own business logic at the GPU level, without forking the native C++ repository.

## 4. Proposed Next Steps (Proof of Concept)

1. **Prototype Triton Primitive**: Port one of the recent complex CuPy RawKernels (such as the exact segment/triangle hitcount filter from Goal 2003 or the exact pairwise Barnes-Hut force accumulator from Goal 1979) to pure Triton.
2. **Performance Audit**: Run a pod artifact pipeline to compare the execution speed, JIT warmup time, and memory usage of the Triton implementation versus the existing CuPy RawKernel baseline.
3. **API Design**: Draft the public Python API surface for the `User-Select-Partner` mode (e.g., `backend="partner_triton"` or allowing users to pass their decorated callable directly into the RTDL continuation pipeline).
