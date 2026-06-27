# Architectural Analysis: The Python + Partner + RTDL Design

**Date:** 2026-05-10
**Author:** Antigravity (Gemini)
**Context:** With the native engine moving towards absolute app-agnosticism (v1.6+), the heavy lifting of domain logic, data materialization, and complex reductions must shift to a "Partner" engine. This report analyzes the choices, the architecture for interoperability, and the strategic recommendation for our first partner.

---

## 1. The Partner: What Choices Do We Have?

The "Partner" is responsible for owning device memory (GPU/CPU tensors) and executing the high-performance business logic *after* RTDL has completed the core spatial queries (`ANY_HIT`, `COUNT_HITS`). 

Our primary candidates in the Python ecosystem are:

1. **PyTorch**: 
   - *Pros*: The undisputed king of AI/ML. Massive mindshare. Excellent GPU memory allocator. Native support for DLPack. Essential if RTDL is to be used for Spatial ML, Graph Neural Networks (PyG), or Autonomous Driving perception pipelines.
   - *Cons*: Heavyweight dependency. Its tensor semantics can sometimes feel overkill for simple relational database grouping.
2. **CuPy**:
   - *Pros*: A drop-in replacement for NumPy on the GPU. Extremely lightweight compared to PyTorch. Excellent for writing custom raw CUDA kernels directly from Python (RawKernel). Perfect for database-style array manipulations.
   - *Cons*: Smaller ecosystem outside of scientific computing.
3. **JAX**:
   - *Pros*: Google's XLA-backed powerhouse. Unbeatable for compiled, pure-functional transformations.
   - *Cons*: Functional purity requirement makes in-place memory mutations (which RTDL might output to) extremely tricky to manage safely.
4. **Numba (CUDA)**:
   - *Pros*: JIT compiles Python into fast CUDA kernels. Great for writing custom business logic without leaving Python.
   - *Cons*: Not a tensor framework per se; lacks the massive pre-built reduction/grouping operations of PyTorch/CuPy.
5. **NumPy**:
   - *Role*: The mandatory CPU-side partner for the `Embree` backend. 

---

## 2. Can We Design an Architecture for Partner Switching?

**YES.** The architecture must be built upon the principle of **Zero-Copy Protocol Standards**. 

If we design this correctly, RTDL C++ will **never** link against `libtorch.so` or CuPy libraries. This prevents vendor lock-in and allows users to switch partners effortlessly.

### The Architectural Blueprint: "The DLPack Bridge"

1. **RTDL Allocates Generic Buffers**: When `rtdl.run_ray_anyhit()` executes, OptiX allocates memory for the results (e.g., an array of hit indices) on the GPU using raw CUDA malloc (or a custom allocator passed via a C-API).
2. **RTDL Exports Standard Protocols**: RTDL wraps this raw GPU pointer in a standard **DLPack** capsule (`__dlpack__`) or the **CUDA Array Interface** (`__cuda_array_interface__`).
3. **Python Facade Passes the Baton**: The RTDL Python wrapper returns this standard object to the user.
4. **User Chooses the Partner**: The user instantly ingests this data into their preferred partner with **zero memory copying**:

```python
# RTDL does the hard spatial math and returns a DLPack object
rtdl_result_dlpack = rtdl.generic_primitives.any_hit(rays, bvh)

# User A prefers PyTorch:
import torch
tensor = torch.from_dlpack(rtdl_result_dlpack)
# Do complex Neural Network inference on the hits...

# User B prefers CuPy:
import cupy
array = cupy.from_dlpack(rtdl_result_dlpack)
# Do fast database-style GroupBy/Sum...
```

**Conclusion on Switching**: By implementing `__dlpack__` and `__cuda_array_interface__` in our Python bindings, the user can seamlessly switch partners line-by-line. RTDL remains a pure "Spatial Primitive Engine," and the partner acts as the "Compute/Tensor Engine."

---

## 3. Which One Should We Choose as Our FIRST One?

For the `v1.7` First Partner Prototype, we must choose **one primary partner** to build our reference architecture, CI/CD testing pipelines, and documentation around.

**Recommendation: PyTorch (Primary) with CuPy (Secondary Validation)**

### Why PyTorch as the First Target?
1. **The Ultimate Stress Test**: PyTorch's memory allocator (caching allocator) is notoriously aggressive. If we can successfully integrate RTDL with PyTorch such that RTDL writes into PyTorch-allocated tensors without causing CUDA illegal memory access or memory leaks, we have proven our architecture is industrial-grade.
2. **Market Dominance**: Integrating with PyTorch immediately unlocks RTDL for the largest demographic of GPU users: ML Engineers and AI Researchers. Applications like `robot_collision_screening` and `ann_candidate_search` directly benefit from PyTorch integration.
3. **Ecosystem Tooling**: PyTorch has robust built-in tools for scatter/gather operations, which are exactly what we need to replace the C++ "App-Leakage" code for Database and Graph analytics. 

### Why CuPy as the "Quiet Validation"?
While PyTorch is the headline partner, we should internally use **CuPy** in our unit tests to validate the `__cuda_array_interface__`. CuPy is lightweight enough to be a fast CI/CD dependency and ensures we haven't accidentally hardcoded PyTorch-specific behaviors into RTDL.

## 4. Next Steps for the Main AI
1. Define the C-API boundary for passing raw pointers/strides out of RTDL OptiX.
2. Implement the `__dlpack__` dunder method in the `rtdsl` Python classes.
3. Write a Proof-of-Concept (Goal 17xx) demonstrating a PyTorch tensor being populated by an RTDL OptiX hit-count operation without any CPU bounce.
