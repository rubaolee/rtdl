# RTDL v2.0 Architectural Direction: Explicit Compute Partnership

**Date:** 2026-04-27
**Author:** Gemini (Antigravity)

## The Core Design Dilemma

As RTDL evolves from its v1.0 hardcoded baseline toward the v2.0 ecosystem, the fundamental question regarding non-ray-tracing (non-RT) application logic—such as filtering, feature extraction, custom physics, or data orchestration—must be answered. 

We face two distinct architectural paths for integrating this logic with RTDL's core traversal engine:

### Path 1: Explicit Compute Partnership (The "Partner" Model)
The user explicitly writes high-performance programs for the non-RT parts using specialized GPU/Compute tools (e.g., OpenAI Triton, CuPy, or PyTorch). RTDL acts as a highly specialized component that hands off data via standard zero-copy protocols (`DLPack`).

### Path 2: Implicit Omnipotent Compilation (The "Magic" Model)
The user writes sequential, naive Python code for the non-RT parts. RTDL attempts to automatically analyze, JIT-compile, parallelize, and fuse this generic Python code with its own RT kernels into a single monolithic execution unit.

---

## The Verdict: Path 1 (Explicit Compute Partnership)

**For RTDL v2.0, we definitively choose Path 1.** 

The goal of v2.0 is to strike the perfect balance between uncompromising hardware performance and simplicity of programming. Attempting to build an omnipotent Python compiler (Path 2) would severely violate this balance.

### Why Path 2 (Implicit Compilation) is Rejected
1. **The Performance Cliff:** "Magic" compilers suffer from severe performance cliffs. When user code strays slightly from the compiler's expected "happy path" (e.g., using an unsupported Python dict or a complex branch), execution falls back to the slow CPU interpreter. This makes debugging performance regressions incredibly painful.
2. **Astronomical Technical Complexity:** Building an AST-parsing, memory-coalescing, automatic-parallelizing Python compiler is the domain of massive standalone projects (like Numba or Jax). RTDL's unique value proposition is *ray-tracing for data*, not reinventing general-purpose compilation.
3. **Ecosystem Isolation:** By trying to do everything natively, RTDL would isolate itself from the rapid advancements in the broader ML/GPU compute ecosystem.

### Why Path 1 (Compute Partnership) is the Right Future
1. **Unix Philosophy applied to GPU Computing:** RTDL does one thing flawlessly: **spatial and graph traversal via Ray Tracing acceleration (BVH/RT Cores)**. By limiting our scope to high-speed traversal and generic scalar reductions (v1.5's `ANY_HIT`, `COUNT_HITS`, `REDUCE`), we keep the engine ABI minimal and robust.
2. **Zero-Copy Handoff via DLPack:** The critical enabler for this path is `DLPack`. When RTDL finishes a complex intersection query, the resulting tensors (e.g., neighbor ID arrays, intersection masks) reside in GPU memory. Through DLPack, these arrays are handed to CuPy or Triton in *O(1)* time with zero memory copy overhead.
3. **Predictable, Explicit Performance:** The user has full agency. They know exactly which phase is accelerated by RT Cores (the RTDL `rt.*` call) and which phase is accelerated by Compute Cores (the Triton kernel or CuPy vectorization). There are no black boxes.

---

## A Glimpse into a v2.0 Application

Under the Explicit Partnership model, a future RTDL v2.0 application separates concerns cleanly:

1. **[Data Preparation - CuPy/PyTorch]** 
   The user loads and prepares geographic points or graph edges on the GPU using standard PyTorch or CuPy operations.
2. **[Ray Tracing Traversal - RTDL]** 
   The user calls an RTDL generic primitive: 
   `intersection_tensor = rt.reduce_float(rt.MIN, scene, rays)`
   RTDL dispatches to NVIDIA RT Cores (OptiX) or CPU BVHs (Embree) and returns a DLPack-compatible tensor.
3. **[Custom Business Logic - Triton/CuPy]** 
   The user passes `intersection_tensor` to a custom `@triton.jit` kernel or a CuPy broadcasting function to calculate losses, filter outliers, or update simulation states directly in GPU memory.

## Conclusion

RTDL v2.0 will embrace **Explicit Compute Partnership**. We will not build a magic compiler. Instead, we will build the most robust, predictable, and performant ray-tracing traversal bridge for Python, designed explicitly to plug into Triton, CuPy, and PyTorch via DLPack. This guarantees that RTDL remains an indispensable, high-performance tool without drowning in compiler technical debt.
