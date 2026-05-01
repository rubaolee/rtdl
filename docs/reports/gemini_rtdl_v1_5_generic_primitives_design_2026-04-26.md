# RTDL v1.5: Generic Reduction Primitives Design

**Date:** 2026-04-26

## 1. Goal
The primary objective of the v1.5 architecture is to achieve **Pragmatic Decoupling**. We must remove all domain-specific logic (e.g., `robot_pose`, `database_scan`, `hausdorff`) from the C++/CUDA engine, replacing them with a generalized spatial reduction pipeline.

The engine should act purely as a high-speed geometry calculator, unaware of the business application driving the queries.

---

## 2. Core Design Pillars

### A. Unified Geometry Interface (Input Lowering)
The C++ engine will no longer accept application structures like `CSRGraph` or `DatabaseTable`. The Python layer must "lower" all data into standardized spatial primitives before calling the engine.

The engine only recognizes:
- `Points` (X, Y, Z)
- `Segments` (P0, P1)
- `Triangles` (P0, P1, P2)
- `Rays` (Origin, Direction, Tmax)
- `AABBs` (MinX, MinY, MinZ, MaxX, MaxY, MaxZ) + Optional Scalar Payload (for SUM/MAX)

### B. The `traverse_and_reduce` API
Instead of dozens of custom entry points, the engine will expose a single, unified kernel API.

```cpp
// Pseudocode for the unified C++ Entry Point
void rtdl_traverse_and_reduce(
    GeometryType build_type,
    void* build_data,
    GeometryType probe_type,
    void* probe_data,
    ReductionOp op,          // <--- The core of v1.5
    void* result_out
);
```

### C. The Standard Reduction Operators (`ReductionOp`)
By implementing a finite set of generic reduction operators inside the OptiX/Embree any-hit and closest-hit programs, we can cover 90% of the current custom workloads.

| Generic Operator | Native Behavior during Traversal | Replaces Current Custom Engine Path |
| :--- | :--- | :--- |
| **`COUNT`** | Increments a counter for every valid intersection. Returns an `int`. | `gap_summary_prepared`, `robot_pose_count`, `segment_polygon_hitcount` |
| **`ANY`** | Terminates traversal on the first hit. Returns a `bool` (1 or 0). | `hotspot_screening`, `ray_triangle_any_hit` |
| **`MIN_DIST`** | Tracks the closest intersection distance. Returns a `float`. | `point_nearest_segment`, `directed_hausdorff_2d_embree` |
| **`SUM_PAYLOAD`** | Accumulates the scalar payload attached to the BVH leaves. Returns a `float`. | `database_grouped_sum` |
| **`COLLECT_K`** | Maintains a bounded priority queue of the top K hits. | `bounded_knn_rows`, `fixed_radius_neighbors` |

---

## 3. How App-Specific Logic is Handled in v1.5

Let's look at how current domain-specific applications will be executed using the generic v1.5 design.

### Example 1: Robot Collision Screening
- **v1.0 (Current):** Python calls `run_robot_pose_count_optix()`. The C++ engine knows about "poses" and "robots".
- **v1.5 Design:** Python lowers the robot arms into generic `Triangles` and the room obstacles into an `AABB` BVH. Python calls `traverse_and_reduce(Triangles, AABBs, op=ANY)`. The engine simply returns an array of booleans (1 if the triangle hit an AABB, 0 otherwise). Python sums the booleans per pose.

### Example 2: Database Grouped Sum
- **v1.0 (Current):** Python calls `run_db_grouped_sum_optix()`. The C++ engine executes a database scan and parses SQL-like clauses natively.
- **v1.5 Design:** Python converts the database rows into `AABBs` (where dimensions represent queried fields like Price or Date). Python attaches the target summation field as a `float payload` to each AABB. Python calls `traverse_and_reduce(Queries, AABBs, op=SUM_PAYLOAD)`. The OptiX engine spatially finds matching rows and sums their payloads in hardware registers.

### Example 3: Hausdorff Distance
- **v1.0 (Current):** C++ engine has a dedicated `directed_hausdorff_2d_embree` endpoint.
- **v1.5 Design:** Python lowers the polygons into `Points` and `Segments`. Python calls `traverse_and_reduce(Points, Segments, op=MIN_DIST)`. The engine returns an array of the shortest distances. Python then takes the `max()` of that array.

---

## 4. Conclusion
The v1.5 design shifts the burden of **Domain Knowledge** back to the Python layer, while retaining the **Reduction Loop** within the C++/CUDA layer. This achieves the exact high performance of v1.0, but restores architectural purity to the RTDL engine.

---

## 5. Extension Mechanisms (When Generic Primitives Fail)

While the 5 generic operators cover most use cases, complex applications may require custom reduction logic that cannot be expressed via basic arithmetic (e.g., custom hashing, complex state machines per ray, or specialized memory allocation).

For v1.5, we propose two extension mechanisms to handle these edge cases without modifying the core engine:

### Option A: Zero-Copy Tensor Handoff (The Python Way)
If the user cannot use `COUNT` or `SUM`, they can instruct the engine to use the `COLLECT_ALL` primitive.
Instead of returning data to the CPU, the RTDL engine writes the raw intersection hits directly into a pre-allocated GPU tensor. RTDL then exports this tensor to Python via **DLPack**.
The user can then write their custom complex reduction logic in **PyTorch, CuPy, or Numba** directly on the GPU without suffering PCIe transfer overhead.

### Option B: Drop-in PTX/SPIR-V Plugins (The C++ Way)
For absolute maximum performance, the RTDL engine will expose a standard **Native Payload ABI**.
1. The user writes a small CUDA or C++ function adhering to a predefined signature (e.g., `void my_custom_hit(HitData* hit, void* user_payload)`).
2. The user compiles this externally into a `.ptx` (for OptiX) or `.so` (for Embree) file.
3. In Python, the user passes the file path: `traverse_and_reduce(..., op="CUSTOM", plugin_path="my_kernel.ptx")`.
4. RTDL dynamically links this kernel into the Any-Hit/Closest-Hit shader pipeline at runtime using `cuModuleLoad` or `dlopen`.

This provides an "escape hatch" for power users to inject custom C++ logic without ever forking or modifying the main RTDL repository.
