# RTDL Feature & Application Analysis Report

**Date:** 2026-04-23
**Scope:** A comprehensive overview of the Ray Tracing Domain Language (RTDL), including its available features, programming model, and target application domains.

---

## 1. Core Philosophy
The Ray Tracing Domain Language (RTDL) is a domain-specific language that maps traditionally non-graphics workloads—such as database queries, graph traversals, and clustering—into highly optimized spatial geometry queries. By doing so, RTDL can dispatch these operations to hardware-accelerated ray tracing engines (like CPU-based Embree or GPU-based OptiX), bypassing the bottlenecks of traditional Python loops, custom tree structures, and unoptimized memory access patterns.

## 2. Language Features (The Core IR & Compiler)
RTDL utilizes a strict pipeline architecture: **Input → Traverse → Refine → Emit**. These core functions are the fundamental building blocks of the language:

*   **`@rt.kernel(backend="...", precision="...")`**: The compiler entry point. It wraps a Python function, captures the AST/operations, and compiles it into Intermediate Representation (IR) targeting a specific hardware engine.
*   **`rt.input(name, geometry, role="...")`**: Defines what data acts as the **probe** (the rays/queries being fired) and what acts as the **build** (the environment bounded into a BVH tree).
*   **`rt.traverse(probe, build, accel="bvh")`**: Instructs the ray tracing engine to perform the heavy lifting of evaluating intersection candidates between the probe and build structures.
*   **`rt.refine(candidates, predicate=...)`**: Applies a specific filtering rule (a predicate from the standard library or custom) to narrow down the candidates to exact matches.
*   **`rt.emit(source, fields=[...])`**: Defines the final schema/columns that should be returned from the C++ boundary back to Python space.

**Execution and Dispatch Features:**
Once defined, a kernel is executed via specific dispatch functions:
*   `rt.run_embree()`, `rt.run_optix()`, `rt.run_vulkan()`, `rt.run_cpu()`: Functions that dynamically compile the kernel for the requested hardware and run it as a "one-shot" query.
*   `rt.prepare_*_dataset(...)`: Creates a persistent, accelerated session that keeps the BVH resident in memory, allowing iterative, high-speed queries without rebuilding the index.

---

## 3. Standard Library (Pre-defined Predicates)
While the *language features* define how to move data, the *Standard Library* provides the actual rules (predicates) used inside `rt.refine()`. These predicates tell the traversal engine exactly what defines a "hit."

### A. Geometric & Intersection Primitives
Used for finding direct physical overlaps between objects.
*   `rt.ray_triangle_any_hit(exact=False)`
*   `rt.ray_triangle_closest_hit()` / `rt.ray_triangle_hit_count()`
*   `rt.segment_intersection(exact=False)`
*   `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`
*   `rt.segment_polygon_hitcount()` / `rt.segment_polygon_anyhit_rows()`
*   `rt.overlay_compose()`

### B. Spatial & Proximity Primitives
Used for discovering neighborhoods and nearest items.
*   `rt.fixed_radius_neighbors(radius, k_max)`
*   `rt.knn_rows(k)`
*   `rt.bounded_knn_rows(k, max_radius)`
*   `rt.point_nearest_segment()`

### C. Graph Analytics Primitives
Used for evaluating graph connectivity by mapping edges to geometry.
*   `rt.bfs_discover(visited, dedupe=True)`
*   `rt.triangle_match(order="id_ascending", unique=True)`

### D. Relational / Database Primitives
Used for executing SQL-like queries over multidimensional datasets.
*   `rt.conjunctive_scan()`
*   `rt.grouped_count()`
*   `rt.grouped_sum()`

---

## 4. Extending RTDL (Writing Custom Libraries)
Developers can extend RTDL by writing their own predicate libraries. In the RTDL Intermediate Representation (IR), a predicate is simply an object wrapping a string identifier and a configuration dictionary.

To create a custom library, a developer defines a standard Python function that returns an `rt.ir.Predicate` object. For example:

```python
import rtdsl as rt
from rtdsl.ir import Predicate

def custom_density_threshold(*, min_points: int, radius: float) -> Predicate:
    # 1. Validate inputs in Python space
    if radius < 0.0:
        raise ValueError("radius must be positive")

    # 2. Return the IR node that the native backend recognizes
    return Predicate(
        name="custom_density_threshold",
        options={
            "min_points": int(min_points),
            "radius": float(radius)
        }
    )
```

**How it works:**
When the `@rt.kernel` compiler encounters this custom predicate inside an `rt.refine()` block, it packages the string `name` and the `options` payload and ships it to the C++ runtime. The user would then implement a matching C++ traversal intersection filter in their backend of choice (e.g., an Embree intersection filter or an OptiX any-hit program) that registers to the string `"custom_density_threshold"`.

---

## 5. Application Domains & Supported Apps
The spatial primitives provided by RTDL generalize elegantly across multiple fields of computer science. The current test suite and examples implement standard algorithms across six distinct domains:

| Domain | Application Example | RTDL Approach |
| :--- | :--- | :--- |
| **Robotics & Kinematics** | `rtdl_robot_collision_screening_app.py` | Maps robot linkage poses to discrete 2D edge rays. Evaluates environmental collisions via `rt.ray_triangle_any_hit`. |
| **Data Mining & Anomaly Detection** | `rtdl_outlier_detection_app.py` | Uses `rt.fixed_radius_neighbors` to natively calculate density counts for millions of points, instantly identifying isolated outliers. |
| **Unsupervised Machine Learning** | `rtdl_dbscan_clustering_app.py` | Uses `rt.fixed_radius_neighbors` to emit "core point flags", offloading the heaviest part of DBSCAN (neighborhood generation) to the BVH. |
| **Computational Geometry** | `rtdl_hausdorff_distance_app.py` | Uses `rt.knn_rows(k=1)` to compute directed maximum distances between complex shapes natively, avoiding massive memory transfers. |
| **Physics & N-Body Simulation** | `rtdl_barnes_hut_force_app.py` | Maps gravity/force quadtree nodes to spatial geometries. Uses `rt.fixed_radius_neighbors` to generate Barnes-Hut opening candidates without O(N^2) checks. |
| **Graph Theory & Networks** | `rtdl_graph_analytics_app.py` | Translates Graph Adjacency / CSR formats into geometry. Evaluates BFS frontiers using `rt.bfs_discover` and counts triangles using `rt.triangle_match`. |
| **Relational Databases & BI** | `rtdl_database_analytics_app.py` | Compiles tabular data into bound spatial boxes. Evaluates `rt.conjunctive_scan` to perform multidimensional `WHERE` clause filtering instantly. |

---

## 6. Architectural Discussion: Engine Purity vs. Performance
A core architectural tension in RTDL is the separation of concerns between the **Ray-Tracing Engine** (Embree, OptiX) and the **Application Domain** (Database, Graph, ML).

**The Ideal: Engine Purity**
Ideally, a pure ray-tracing engine should be entirely blind to the domain. It should never see a concept called `hausdorff` or `bfs_discover`. It should only be told: *"Here is a BVH of points. Here is a probe. Find the 1 nearest neighbor."* What that neighbor *means* is the application's responsibility.

For the most part, RTDL adheres to this philosophy. For example, using `rt.knn_rows(k=1)` or `rt.fixed_radius_neighbors`, the engine operates purely on geometric abstractions. It blindly returns spatial hits, and Python derives the meaning (e.g., classifying a hit as a "robot collision" or an "outlier").

**The Reality: The Abstraction Leak**
However, the abstraction currently "leaks" in several high-performance native paths, such as `rt.directed_hausdorff_2d_embree`, `rt.prepare_embree_db_dataset`, and `rt.fixed_radius_count_threshold_2d_embree`.

This leakage is a direct result of **Python overhead**. If RTDL strictly relies on pure spatial queries, the C++ engine must serialize and transfer millions of individual intersection rows back to Python. Python then iterates that massive array to perform a simple reduction (like a `max()` for Hausdorff, or a `sum()` for DBSCAN densities). The BVH traversal is lightning-fast, but materializing millions of Python objects bottlenecks the entire application. To achieve benchmark speeds, the RTDL team hardcoded these domain-specific reductions directly into the C++ engine boundary.

**The Ultimate Solution**
To resolve this tension, the ultimate vision for RTDL is to mature its **Intermediate Representation (IR) Compiler**:
1. The user writes high-level domain logic.
2. The RTDL compiler breaks that logic down into pure, generic geometric operations (keeping the engine blind).
3. The compiler *automatically generates* the native C++ reduction code (e.g., the `max()` accumulator) to run immediately after the engine traversal, keeping the intermediate data in fast native memory without hardcoding domain concepts into the core engine.

## Summary
RTDL represents a bridge between high-level analytical Python code and low-level hardware-accelerated rendering APIs. By expressing domains like databases, physics, and graphs in a spatial `probe-and-build` vocabulary, developers gain access to massive parallel performance scaling (via Embree CPU or OptiX GPU) without writing C++ or CUDA kernels by hand.
