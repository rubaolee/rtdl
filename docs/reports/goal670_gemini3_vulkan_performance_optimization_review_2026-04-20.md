# Goal670: Vulkan Performance Optimization Review

Date: 2026-04-20

## Review of Goal669 Playbook against Vulkan Backend

Based on the cross-engine performance optimization lessons from Apple RT (Goal 669) and the current state of the Vulkan backend, here are the identified optimization opportunities for Vulkan:

### 1. Acceleration Structure (BVH) Caching
- **Current State:** The Vulkan backend currently rebuilds the Top-Level Acceleration Structure (TLAS) and Bottom-Level Acceleration Structure (BLAS) on every call (no persistent scene caching).
- **Opportunity:** Implement persistent BLAS/TLAS caching for static geometry (e.g., caching the polygon BVH across multiple point-in-polygon queries). This aligns with the "Context Reuse" strategy and will drastically reduce GPU upload and BVH build times on repeated execution paths (as highlighted by the Goal 88 long exact raw-input measurements where Vulkan is still much slower than PostGIS/OptiX).

### 2. Pre-computed Workload Capacity and Output Materialization
- **Current State:** Vulkan allocates worst-case `O(N * M)` buffers for workloads like `lsi` (`left_count * right_count`) and `pip` (full matrix `npoints * npolygons`). This causes Vulkan to hit the 512 MiB output guardrail on long exact-source surfaces (Goal 85).
- **Opportunity:** Adopt the "Pre-computed Workload Capacity" strategy. Implement a two-pass approach in Vulkan (or use an atomic counter with a tightly bounded, host-read compact buffer) to avoid allocating catastrophic `O(N * M)` memory. This is the primary blocker preventing Vulkan from joining the long exact-source comparison row.

### 3. Broadening Native Early-Exit (Any-Hit)
- **Current State:** Goal 650 successfully upgraded `ray_triangle_any_hit` to use native early-exit (`terminateRayEXT`).
- **Opportunity:** Extend native early-exit to other any-hit queries like `segment_polygon_anyhit_rows`. Currently, the architecture supports early-exit on ray-triangle, but applying this systematically to all boolean/any-hit predicates will yield dense-hit traversal improvements.

### 4. Native Jaccard Kernels
- **Current State:** The Vulkan backend currently falls back to the native CPU oracle for Jaccard workloads (`polygon_set_jaccard`, `polygon_pair_overlap_area_rows`) to maintain honesty.
- **Opportunity:** Implement native Vulkan device kernels for the Jaccard workloads, moving them off the CPU oracle and enabling hardware acceleration for these complex geometries.

### 5. Descriptor/Buffer Reuse
- **Current State:** Each workload call allocates a transient descriptor set (one pool per call, destroyed after submission).
- **Opportunity:** Pool and reuse descriptor sets and staging buffers across calls to reduce CPU overhead during `vkAllocateDescriptorSets` and memory mapping.

## Risks and Blockers

- **Catastrophic Memory Guardrails:** The current worst-case `O(P x Q)` memory allocation contract is a hard blocker. Until a sparse or two-pass materialization is implemented, Vulkan cannot run the long exact-source county/zipcode packages. Claims of large-scale scaling must be blocked until this is addressed.
- **Driver Variability:** Vulkan KHR ray tracing behavior and compilation (via `shaderc`) can vary across drivers (e.g., NVIDIA vs AMD vs Intel). Optimization on one vendor's driver might not uniformly translate to others, requiring broad hardware validation.
- **Synchronous Execution:** All work is submitted to a single queue with `vkQueueWaitIdle`. Overlapping CPU preparation with GPU execution would be needed for maximum throughput.

## Verdict

`ACCEPT`. The Goal 669 playbook translates exceptionally well to the Vulkan backend. Addressing the BVH caching and worst-case output buffer allocation will resolve the primary bottlenecks blocking Vulkan from matching OptiX, Embree, and PostGIS on long execution surfaces.
