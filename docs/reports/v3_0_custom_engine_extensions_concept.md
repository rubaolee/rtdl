# Concept & Planning: RTDL v3.0 Custom Engine Extensions

**Date:** 2026-05-11
**Status:** Exploratory / Long-Term Planning

## 1. Background & Motivation
During the rigorous v1.6 to v1.8 release cycle, the RTDL Native Engine was structurally decoupled from all domain-specific application logic (Database, GIS, Graph, etc.). The C ABI was reduced to 100% app-agnostic primitives (e.g., `columnar_payload`, `multi_predicate_scan`, `frontier_edge_traversal`).

While this decoupling was primarily aimed at architectural purity and maintainability, it unintentionally unlocked a "Holy Grail" capability for the framework: **Custom Engine Extensions**. By treating the engine as a pure, mathematically agnostic "motherboard," we can now introduce "PCIe-like slots" where developers can plug in their own custom hardware-accelerated logic.

## 2. The Core Concept
Just as PyTorch allows for custom C++/CUDA extensions, and Triton allows developers to write custom GPU kernels, RTDL v3.0 should allow users to write their own **Custom Ray Tracing Extensions**. 

Instead of waiting for the core RTDL team to implement specific domain logic, developers can write their own spatial filters, custom payload handlers, or collision algorithms, and inject them dynamically into the RTDL BVH and ray-dispatch pipeline.

## 3. Proposed Architecture Mechanism

### A. The "Pure" Motherboard
The native C++ core will remain completely locked down and agnostic. It will only handle:
- Device Context & GPU Memory Management
- High-Performance BVH (Bounding Volume Hierarchy) Building
- Massively Parallel Ray Dispatch

### B. Payload "Slots"
Structures like `columnar_payload` will serve as standardized memory layouts. Developers can pack their arbitrary data (astronomy coordinates, financial time-series, fluid dynamics particles) into these standardized payload slots without modifying the engine.

### C. Dynamic Custom Shader Injection
The true power of v3.0 will be exposing the Ray Tracing Shader boundary to the user. Developers can write their own intersection or any-hit logic using native backend languages:
- **OptiX:** Custom CUDA `.ptx` files.
- **Vulkan:** Custom GLSL/HLSL compiled to `.spv` bytecode.
- **Apple RT:** Custom Metal Shading Language `.metallib` kernels.

### D. The Python Extension API
At the Python layer, users will dynamically load and bind their compiled shaders to the RTDL core execution loop.

```python
import rtdl as rt

# 1. Load the user's custom astronomy physics shader
astro_extension = rt.load_extension("astro_collision_shader.ptx")

# 2. Pack domain data into a generic payload slot
payload = rt.create_columnar_payload(stars_data_tensor)

# 3. Dispatch the ray tracing engine with the custom extension
results = rt.run_custom_scan(payload, extension=astro_extension)
```

## 4. The Future: JIT Compilation
The ultimate evolution of this extension API would be Python-side Just-In-Time (JIT) compilation. Similar to OpenAI's Triton, users could write their custom ray intersection logic directly in Python. The RTDL Python wrapper would JIT-compile this into the appropriate `.ptx` or `.spv` bytecode behind the scenes and hot-swap it into the running engine, completely democratizing access to hardware-accelerated BVH compute.

## 5. Conclusion
The massive, painful refactoring efforts of v1.8 (stripping `db`, `polygon`, `knn` from the native core) are exactly what makes this v3.0 vision possible. A polluted core engine could never support third-party plugins. A perfectly pristine geometric core can support the entire world's custom logic.
