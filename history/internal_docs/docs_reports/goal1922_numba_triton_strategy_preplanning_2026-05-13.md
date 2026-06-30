# Goal1922 - Numba/Triton Strategy Pre-Planning

Status: exploratory-roadmap-note

Date: 2026-05-13

## Context

RTDL v2.0 is focused on Python+partner+RTDL:

- RTDL provides app-agnostic RT primitives.
- PyTorch is the reference partner path.
- CuPy is the conformance partner path.
- Python remains the app orchestration and semantic layer.
- Users compose RTDL output columns with partner tensor operations.

The question is where Numba, Triton, CuPy `RawKernel`, or similar user-written
GPU kernels belong.

## Recommendation

Do not make Numba, Triton, or CuPy `RawKernel` part of the v2.0 release
contract.

Instead:

- v2.0: partner tensor composition only.
- v2.5: external custom-kernel interop examples.
- v3.0: possible custom engine/shader extension ABI.

## v2.0 Boundary

In v2.0, users should write:

```python
hits = rtdl.optix.count_hits(..., output="torch")
scores = torch.log1p(hits.float()) * weights
top = torch.topk(scores, k=128)
```

They should not need to write CUDA, Triton, Numba, OptiX shader code, or CuPy
raw kernels to benefit from RTDL.

This keeps v2.0 clean:

- RTDL engine stays app-agnostic.
- Partner tensor APIs provide general-purpose post-RT computation.
- The release can be explained as Python eDSL + generic RT primitives + tensor
  programming.
- No user-defined kernel ABI is needed.

## v2.5 Candidate: External Kernel Interop

v2.5 can document and test optional external kernel interop:

```python
hits = rtdl.optix.count_hits(..., output="torch")
scores = my_triton_kernel(hits, weights)
```

or:

```python
hits = rtdl.optix.count_hits(..., output="cupy")
scores = my_cupy_rawkernel(hits, weights)
```

The important boundary is that these kernels run after RTDL and outside the
RTDL native engine. RTDL only promises compatible tensor layout, ownership, and
lifetimes for the output columns.

This would require:

- examples for Triton and/or Numba consuming RTDL output tensors;
- clear device, dtype, stride, lifetime, and synchronization rules;
- tests proving RTDL output tensors can be consumed by external kernels;
- public wording that this is interop, not engine extension.

Triton is likely the stronger first candidate because it aligns naturally with
PyTorch and GPU-first tensor kernels. Numba may still be useful for CPU/CUDA
experimentation, but it should not define the RTDL partner ABI.

## v3.0 Candidate: Engine Extensions

Deep custom kernel integration belongs in v3.0 or later. This includes:

- user shader slots;
- custom OptiX PTX, Vulkan SPIR-V, or Apple Metal injection;
- Triton/Numba-generated kernels participating in RTDL execution plans;
- engine-side payload schemas;
- versioned extension ABI;
- safety/isolation policy;
- per-backend conformance tests.

This is much larger than v2.0. It changes RTDL from a generic RT primitive
language into a custom engine-extension platform.

## Strategic Rule

v2.0 should prove that Python users can build serious RT-heavy programs by
composing:

- RTDL generic RT primitives;
- PyTorch/CuPy partner-owned tensors;
- ordinary partner tensor operations.

Only after that is proven should RTDL introduce optional external kernel
interop in v2.5, and only after that should it consider custom engine
extensions in v3.0.

## Current Release Impact

This note does not change v2.0 release criteria. It is a pre-planning document
only. The active v2.0 blockers remain:

- Claude or Pro-class review of actual pod artifacts;
- final source-tree/package decision consensus;
- final v2.0 release consensus;
- explicit release action.
