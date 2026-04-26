# RTDL Architectural Interim Solutions: Decoupling Engine Purity from Native Performance

**Date:** 2026-04-26

## 1. Context and the Core Problem

The RTDL ecosystem is currently wrestling with a fundamental architectural tension: **Engine Purity vs. Native Performance**.

While the hardware RT Cores (OptiX) are exceptionally fast at executing spatial intersections and bounds checks, they generate massive volumes of intermediate row data (e.g., millions of overlapping boundary pairs). If this raw data is transferred back to host memory and serialized for a Python `for` loop to perform simple aggregations (like counting, finding the minimum distance, or boolean reductions), the **I/O data transfer and Python execution overhead entirely negate the hardware acceleration.**

### The Current Workaround
To survive this bottleneck, RTDL currently relies on **"Customized Engines."** The system hardcodes domain-specific application logic directly into the C++ / CUDA engine (e.g., `directed_hausdorff_2d_embree` or hotspot screening logic). The engine intercepts the intersection results natively, performs the reduction on the GPU, and returns only a tiny scalar back to Python.

> [!WARNING]
> **The Cost of the Workaround**
> This pollutes the engine. A spatial traversal engine should not "know" about Hausdorff distances, facility assignments, or DBSCAN clustering. This creates a maintenance burden where every new application requires writing and compiling a custom C++ engine path.

While the long-term vision is to utilize a **CUDA Partner (like Numba or Triton)** to compile Python logic into GPU-native reductions, that integration will take time. This report proposes four interim solutions to bridge the gap, maximizing performance while returning the RT engine to a state of domain-agnostic purity.

---

## 2. Proposed Interim Solutions

### Solution A: Generic Reduction Primitives
Instead of hardcoding specific business domains into the engine, we can abstract the mathematical operations. The engine exposes a generic `traverse_and_reduce()` pipeline.

- **Mechanism:** The Python layer configures a query (e.g., "ray cast") and pairs it with a native reduction primitive like `MIN`, `MAX`, `SUM`, `COUNT`, or `ANY` (boolean).
- **Execution:** The engine traverses the space natively, applies the basic mathematical reduction on the fly, and returns the final aggregate.
- **Why it works:** The engine remains completely blind to the *meaning* of the data (it doesn't know it's calculating "Hausdorff distance," it only knows it's computing a generic `MAX(MIN)` spatial reduction).

### Solution B: Zero-Copy Vectorization (DLPack / Apache Arrow)
If massive amounts of intermediate intersection data *must* be returned to Python, the primary bottleneck is memory serialization and the Python native loop, not the actual mathematical computation.

- **Mechanism:** The engine returns results using zero-copy formats like **DLPack** (for in-place GPU tensor sharing) or **Apache Arrow** (for highly efficient columnar host data).
- **Execution:** Python receives a pointer to the data instantly. The application then uses vectorized libraries (`NumPy`, `Pandas`, or `CuPy`) to execute the reduction in C/CUDA space.
- **Why it works:** It entirely bypasses Python serialization and `for`-loop overhead.

### Solution C: Lazy Execution Graph (AST Parsing)
Similar to modern data processing frameworks (like Polars or PyTorch), RTDL could delay execution until the entire pipeline is defined.

- **Mechanism:** The Python app builds a chain of operations: `rt.intersect().filter(dist < 5.0).count()`. Instead of executing immediately, Python builds an Abstract Syntax Tree (AST) or computation graph.
- **Execution:** The entire graph is handed to the backend. The backend's query planner allocates a single native C++ pipeline to execute the traversal, filter, and count in one native sweep.
- **Why it works:** Python acts purely as an orchestrator and graph-builder. The heavy lifting is executed seamlessly within the native bounds.

### Solution D: Lightweight DSL / JIT Injection
OptiX and modern rendering pipelines are already designed around compiling PTX code dynamically.

- **Mechanism:** The Python application provides a minimal Domain-Specific Language (DSL) string or mathematical expression (e.g., `"return dist < threshold ? 1 : 0;"`).
- **Execution:** The engine dynamically injects this string into the C++ / CUDA kernel via a lightweight JIT (Just-In-Time) compiler like `shaderc` or NVRTC (NVIDIA Runtime Compilation) right before executing the traversal.
- **Why it works:** Developers can write custom reduction logic dynamically without having to modify or recompile the core RTDL engine source code.

---

## 3. Conclusion and Recommendations

> [!TIP]
> **Recommended Path Forward**
> For the highest immediate Return on Investment (ROI) with the lowest engineering risk, RTDL should adopt a hybrid of **Solution A (Generic Reduction Primitives)** and **Solution B (Zero-Copy DLPack)**.

By implementing 4 to 5 basic reduction operations (`MIN`, `MAX`, `SUM`, `COUNT`, `ANY`) directly inside the engine, we can eliminate 80% of the current hardcoded custom application endpoints. For the remaining 20% of highly complex applications that require bringing row-data back to the application layer, returning DLPack tensors will allow fast, vectorized NumPy/CuPy post-processing, successfully decoupling the engine from the business logic until a mature Triton/Numba partner integration is achieved.

---

## 4. Addendum: The v1.0 vs v2.0 Roadmap and Compute Graph Challenges

Following an architectural review, it has been established that while **Solution C (Lazy Execution Graph)** represents the conceptual "Holy Grail" for RTDL, it introduces severe near-term engineering blockers.

### Why the Compute Graph is Exceptionally Difficult for RTDL
While constructing an Abstract Syntax Tree (AST) in Python is trivial, executing it natively in the C++/CUDA backend presents massive hurdles:

1. **Combinatorial Explosion vs. Compilation Constraints**: Unlike simple reduction primitives, a compute graph allows infinite combinations of nodes. Pre-compiling all permutations using C++ templates would balloon compilation times and the final library binary size (`.so`) to unmanageable levels.
2. **GPU Branch Divergence**: Implementing a dynamic graph "interpreter" within a CUDA kernel (e.g., executing massive `if-else` blocks for node types) causes severe Warp Divergence, destroying the parallel performance of RT Cores.
3. **The Need for a Full JIT Compiler**: The only performant way to execute arbitrary ASTs on the GPU is to translate the graph into CUDA strings and compile them dynamically at runtime (via NVRTC). This effectively requires building a custom compiler backend (similar to TensorFlow XLA or PyTorch Inductor), which is a multi-year engineering effort.

### The Phased Roadmap
To balance stable release timelines with long-term architectural ambition, RTDL will adopt the following three-phase approach:

- **v1.0 (Stabilize Current Architecture)**: Maintain the current **"Customized Engines"** approach. Because the primary goal of v1.0 is to prove the raw performance viability of the RT Cores across the current flagship demos, introducing architectural overhauls right before the release is risky. The hardcoded business logic stays for now to guarantee maximum throughput and stability for the release benchmarks.
- **v1.5 (Pragmatic Decoupling)**: Transition to **Solution A (Generic Reduction Primitives)**. Hardcoding 4-5 fundamental math operations (`SUM`, `MIN`, `MAX`, `COUNT`, `ANY`) inside the engine provides 80% of the architectural decoupling. This effectively cleans up the technical debt by removing application-specific logic (e.g., `hotspot_screening`) from the core traversal engine.
- **v2.0 (The Compute Partner Ecosystem)**: Defer the compute graph complexity to external ecosystem tools. By leveraging mature **Compute Partners** (such as Triton or Numba), RTDL can offload dynamic code generation and AST compilation to dedicated compiler ecosystems, allowing the RTDL engine to permanently remain a pure, hardware-agnostic spatial traversal tool.
