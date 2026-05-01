# Goal 694: True RT-Core Redesign Plan for Compute-Bound Apps

**Date**: 2026-04-21
**Evaluator**: Gemini (AI Agent)

## 1. Executive Summary

The current `cuda_through_optix` applications (Hausdorff, ANN, Outlier, DBSCAN, Barnes-Hut) rely on standard parallel CUDA compute algorithms (`knn_rows` and `fixed_radius_neighbors`). While fast, they do not utilize the dedicated Ray Tracing hardware (RT Cores) present in NVIDIA RTX GPUs.

To achieve "True RT-Core Acceleration," we must map these point-based distance algorithms to the formal primitives that RT Cores understand natively: **Axis-Aligned Bounding Box (AABB) intersection and Ray-Primitive intersection**.

This report details the architectural redesign necessary to translate these math problems into geometric ray-tracing problems, effectively tricking the RT Cores into executing $O(N \log N)$ distance spatial queries in hardware.

---

## 2. The Paradigm Shift: The "2.5D Orthogonal Ray" Mapping

RT Cores are strictly designed to trace 1D rays through 3D space. Nearest-neighbor and fixed-radius queries lack a spatial "direction." To bridge this gap, we will use a **2.5D Orthogonal Projection Mapping**:

### The Fixed-Radius Mapping Mechanism
For a given 2D dataset and a search radius $R$:
1. **The Scene (Database):** Every database point $(x_i, y_i)$ is geometrically modeled as a 3D sphere centered at $(x_i, y_i, 0)$ with a radius of $R$.
2. **The Hardware BVH:** OptiX natively builds a hardware BVH over the AABBs of these spheres: `[x-R, x+R]`, `[y-R, y+R]`, `[-R, R]`.
3. **The Traversal (Query):** Every query point $(q_x, q_y)$ casts a 1D orthogonal ray starting at $(q_x, q_y, -R)$ shooting straight up in the direction of $+z \ (0,0,1)$.
4. **RT-Core Execution:** If the Euclidean distance between the query and a database point is $\le R$, the ray will perfectly intersect the 3D sphere. The RT Core's hardware BVH intersection engine automatically culls all points further than $R$, reducing an $O(N^2)$ compute workload into a zero-waste RT-Core traversal.

---

## 3. App-by-App Redesign Plan

### 1. Outlier Detection (`rtdl_outlier_detection_app`)
*   **Target Problem**: Find points with `< min_neighbors` within `radius`.
*   **RT-Core Design**: Use the 2.5D Orthogonal Ray mapping with the sphere size set to the `radius`.
*   **Execution**: Launch one ray per query point. Instead of emitting payloads for each hit, the custom `any_hit` or `closest_hit` OptiX shader maintains a simple integer counter.
*   **Native Output**: A flat array of `neighbor_count` per point. Python applies the `is_outlier = count < min_neighbors` threshold.
*   **Result**: 100% RT-Core utilization; zero Python dict-row overhead.

### 2. Barnes-Hut Force Simulation (`rtdl_barnes_hut_force_app`)
*   **Target Problem**: Apply gravitational force from Quadtree nodes. The "Opening Rule" states a node is approximated as a point mass if `size / distance < theta`.
*   **RT-Core Design (The "Opening Sphere")**: We flip the opening rule to a distance threshold: `distance > size / theta`.
    *   Initialize each Quadtree node as a 3D sphere with radius `R = size / theta`.
    *   Query bodies cast the standard 2.5D $(0,0,1)$ orthogonal ray.
*   **Execution**: If the body's ray HITS the node's sphere, the node is "too close" and must be opened (traversed deeper). If the ray MISSES, the RT Core automatically rejects the AABB, meaning the node satisfies the approximation rule. OptiX payloads directly sum the `mass` and `center_of_mass` for all missed nodes.
*   **Result**: The RT Core hardware natively resolves the Barnes-Hut opening logic.

### 3. DBSCAN Clustering (`rtdl_dbscan_clustering_app`)
*   **Target Problem**: Phase 1 requires identifying Core Points (dense neighborhoods within `epsilon`).
*   **RT-Core Design**: Identical to Outlier Detection mapping where sphere size = `epsilon`.
*   **Execution**: Terminate traversing the ray payload early once `count >= min_points` (utilizing OptiX `optixTerminateRay`).
*   **Native Output**: A binary array `is_core_point`.
*   **Result**: O(N) Python time is strictly spent on cluster linkage, completely offloading the heavy density identification to the RT Cores.

### 4. Hausdorff Distance (`rtdl_hausdorff_distance_app`)
*   **Target Problem**: Maximum of the shortest distances (a global KNN problem).
*   **RT-Core Design**: Since RT Cores don't do native KNN radius expansion easily, we reconstruct this as a **Binary Search Ray Query**.
*   **Execution**:
    1. Guess a Hausdorff distance $R$.
    2. Build the BVH with spheres of radius $R$.
    3. Launch orthogonal rays for all points. Use OptiX `any_hit` which is heavily optimized for binary queries.
    4. If *all* rays hit a sphere, $R$ is too large (or perfect). If *any* ray misses, $R$ is too small.
*   **Result**: 10-20 BVH rebuilds + traversal passes in hardware is drastically faster than $O(N^2)$ software compute for large datasets.

### 5. ANN Candidate Search (`rtdl_ann_candidate_app`)
*   **Target Problem**: Ranking a candidate subset of approximate neighbors.
*   **RT-Core Design**: Since the candidate subset is small, replace the 1D CUDA distance search with short spherical bounding queries over the subset BVH.
*   **Execution**: Use `optixTrace` to evaluate local spherical intersections, outputting a native memory array of top-K IDs.

---

## 4. Implementation Action Steps

1.  **Phase 1: The Primitive Layer**
    *   Write the custom PTX intersection program for `Ray-Sphere` bounding (mapping `(q_x, q_y)` to `(x_i, y_i)`).
    *   Update the RTDL core engine to support injecting variable $R$ sizes into the AABB BVH builder.
2.  **Phase 2: App Conversion (Low Hanging Fruit)**
    *   Implement **Outlier Detection** and **DBSCAN Core Point Discovery** using the constant-R 2.5D orthogonal ray method.
    *   Replace `tuple[dict, ...]` returns with `ctypes` native contiguous memory arrays.
3.  **Phase 3: Deep Refactoring**
    *   Implement the **Barnes-Hut** opening-rule sphere intersection shader.
    *   Implement the Hausdorff Binary-Search control loop inside the Python wrapper calling the native OptiX launch.
4.  **Phase 4: Hardware Measurement**
    *   Run the suite on an Ampere/Ada GPU (e.g., RTX 3080 or RTX 4090) utilizing the `goal691` phase profiler to prove that `native_execute` times scale differently than standard CUDA SIMT execution.

---

*This plan shifts the RTDL optimization boundary from simple "Interface Packing Fixes" into "Algorithmic Translation for Custom Silicon", establishing a massive, defensible technical moat for the platform.*
