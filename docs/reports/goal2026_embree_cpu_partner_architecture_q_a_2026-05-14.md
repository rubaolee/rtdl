# Goal 2026 Q&A: Embree and CPU Partner Layer Architecture in v2.0

**Date**: 2026-05-14
**Author**: Gemini/Antigravity (User Q&A Record)
**Status**: informational

## Question

In RTDL v2.0, the OptiX pipeline relies on the GPU (NVIDIA) and passes data to a GPU-based partner layer (CuPy/PyTorch) to achieve "true zero-copy" app continuations. However, our Embree engine runs on Intel CPUs. If the native engine is Embree and we don't have a GPU, how does the v2.0 Python+Partner architecture actually work?

## Answer

The short answer is that **the core v2.0 architectural philosophy remains completely identical**, but the physical execution environment shifts from the GPU (VRAM) to the CPU (Host RAM). The "zero-copy" boundary and the strict separation of concerns are fully preserved.

Here is the breakdown of how the Embree/CPU pipeline functions under the v2.0 paradigm:

### 1. Calculation Venue Shift (The Backend)
The Native -> Partner handoff happens exactly the same way, just in different memory spaces:
- **OptiX (GPU) Pipeline**: OptiX (Native) -> VRAM Pointers -> CuPy / Torch-GPU (Partner).
- **Embree (CPU) Pipeline**: Embree (Native) -> Host RAM Pointers -> **NumPy / Torch-CPU (Partner)**.

### 2. Preserving "Host Zero-Copy"
A common pitfall in C++/Python integrations is copying C++ arrays into Python lists, which destroys performance. RTDL avoids this entirely. 

When Embree generates the raw `(ray_id, primitive_id)` witness pairs in C++ heap memory, RTDL directly grabs the memory pointers. Using the standard Buffer Protocol (e.g., NumPy's `__array_interface__` or PyTorch's `torch.from_blob`), RTDL **wraps** the raw C++ memory directly into a NumPy array or a PyTorch CPU tensor *in-place*. The data is never duplicated.

### 3. Operator Polymorphism
The RTDL user experience remains seamless because the high-level partner operators (e.g., `partner_group_count_by_key`) are polymorphic. 
- If the user is running an OptiX backend, the operator internally dispatches to `cupy.bincount` or `torch.bincount(device='cuda')`.
- If the user is running an Embree backend, the exact same operator simply dispatches to `numpy.bincount` or `torch.bincount(device='cpu')`.

The user's app-level code does not need to change.

### 4. Custom User Primitives on CPU (User-Select-Partner)
Just as we proposed introducing Triton for custom GPU operations (avoiding CuPy RawKernel C++ strings), the CPU pipeline has its own equivalent.

If a user needs a highly specialized domain continuation on the CPU and standard NumPy tensor math isn't expressive enough, they do not need to write C++. Instead, they can use **Numba (CPU)**. By simply writing a pure Python function and decorating it with `@numba.jit`, Numba will compile it to highly optimized LLVM machine code that traverses the zero-copy Embree memory directly. Cython is also a valid alternative. 

## Conclusion
For Embree and CPU environments, the v2.0 native engine remains purely a generic geometric candidate producer, and the partner layer continues to hold all domain semantics. The only difference is that the "zero-copy bridge" connects C++ Host RAM to NumPy/Torch-CPU, rather than C++ VRAM to CuPy/Torch-GPU.
