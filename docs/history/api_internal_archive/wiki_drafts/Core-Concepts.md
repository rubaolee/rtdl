# Historical Wiki Draft Note

This page was imported from a parallel checkout on 2026-04-10 as a preserved
draft artifact. It is **not** the current live source of truth for RTDL docs.
For current language docs, start at [docs/rtdl/README.md](../rtdl/README.md).

---

# Core Concepts: The RTDL DSL

RTDL provides a Python-based Domain Specific Language (DSL) that allows you to specify what data you want to query, without worrying about how the search is accelerated.

## 1. The Kernel
An RTDL program is centered around a `@rt.kernel`. This function defines the data flow and query logic.

```python
import rtdsl as rt

@rt.kernel(backend="rtdl")
def overlap_kernel():
    # Define Inputs
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    
    # Accelerated Traversal (BVH)
    candidates = rt.traverse(left, right, accel="bvh")
    
    # Refinement Predicate
    refined = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows())
    
    # Record Emission
    return rt.emit(refined, fields=["left_id", "right_id", "area"])
```

## 2. Roles: Probe vs. Build
In geometric queries, roles are critical for performance:
*   **Build**: The "geometry set" that is indexed (usually the larger or static set). A Bounding Volume Hierarchy (BVH) is built over this set.
*   **Probe**: The "query set" that searches the Build set (e.g., rays moving through a scene, or segments being joined against polygons).

## 3. The Lifecycle
1.  **Declaration**: Define your inputs and kernel logic using the `rtdsl` API.
2.  **Compilation**: `rt.compile_kernel()` converts the Python DSL into an Internal Representation (IR).
3.  **Lowering**: `rt.lower_to_execution_plan()` transforms the IR into a specific sequence of native calls or vendor-specific packets.
4.  **Execution**: `rt.run_embree()` or `rt.run_optix()` executes the plan against real data.

## 4. Portability
The same kernel can be run on the CPU (using Python or Native C++/Embree) and the GPU (OptiX/Vulkan) simply by changing the runner function. Parity is enforced by the system, ensuring consistent results across all hardware.
