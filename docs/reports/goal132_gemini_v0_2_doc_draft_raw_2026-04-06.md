# Goal 132 Artifact: Gemini v0.2 User Doc Draft (Raw)

Date: 2026-04-06
Status: raw draft

Below is the raw Gemini draft that was used as the starting point for the final
reviewed v0.2 user guide.

---

# RTDL v0.2 Draft

## What Is New
RTDL v0.2 marks a transition from a bounded, RayJoin-centered research tool to a broader programmable system for non-graphical ray-tracing workloads. The release is defined by a "new-workload-first" strategy, successfully closing the **Segment/Polygon Hit Count** family with full backend parity and performance maturation. Additionally, v0.2 introduces a **Generate-Only** mode, allowing users to emit runnable code artifacts without local execution. The system now features a more disciplined scope charter, a stronger feature-product surface for user-facing examples, and an optimized candidate-index strategy across all backends.

## Workloads
RTDL v0.2 supports a growing library of non-graphical spatial workloads:
*   **Segment/Polygon Hit Count (v0.2 Flagship):** Counts intersections between probe segments and build polygons; validated against PostGIS for large-scale correctness.
*   **Segment/Polygon Any-Hit Rows:** Emits raw (segment, polygon) pairs for every true intersection, suitable for join-style auditing.
*   **PIP (Point-in-Polygon):** Determines if probe points are contained within build polygons (currently supports "inclusive" boundary mode).
*   **LSI (Line Segment Intersection):** Identifies intersections between two sets of segments.
*   **Point/Nearest Segment:** Finds the closest build segment for every probe point, including distance metrics.
*   **Ray/Triangle Hit Count:** Statistical counting of ray-triangle intersections.
*   **Overlay (Seeds):** Identifies candidate pairs for polygon overlay; emits a schema indicating where LSI or PIP refinement is required.

## Generate-Only
The new **Generate-Only** mode is a secondary product line designed for handoff workflows. In this mode, RTDL functions as a compiler that emits a standalone, runnable Python artifact. A typical generated bundle includes:
*   The optimized RTDL kernel source.
*   A driver/main program tailored to the workload.
*   The accepted emitted target shape.
*   A verification stub or "golden-example" harness for local validation.
This mode is intentionally narrow to ensure that all generated code is verified and technically sound rather than mere boilerplate.

## Platforms
RTDL remains a Python-hosted DSL that targets high-performance ray-tracing backends:
*   **Native C/C++ Oracle:** The trusted host-side reference for correctness.
*   **Embree:** A production-quality CPU baseline and primary fallback.
*   **OptiX:** The high-performance path utilizing NVIDIA RT cores for hardware-accelerated traversal.
*   **Vulkan:** A hardware-validated portability backend that ensures parity across different GPU vendors, though currently prioritized for correctness over raw speed.

## Backend Notes
Significant infrastructure improvements have been implemented in v0.2 to support new workloads:
*   **Candidate-Index Redesign:** A new indexing strategy (bounding box x-range filtering) has been implemented for CPU, Embree, and Vulkan to reduce redundant exact-refine work.
*   **OptiX Alignment:** The OptiX backend has been aligned with the host-indexed candidate strategy to maintain performance parity on large deterministic Linux workloads.
*   **Performance Characterization:** v0.2 features deep performance audits for `segment_polygon` workloads, showing strong competitiveness against indexed PostGIS queries on prepared/repeated boundaries.

## Quick Start
To define a kernel, use the `@rt.kernel` decorator in Python:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_hazard_screening():
    roads = rt.input("roads", rt.Segments, role="probe")
    hazards = rt.input("hazards", rt.Polygons, role="build")
    candidates = rt.traverse(roads, hazards, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

Run the kernel using your preferred backend:
```python
# Oracle
rows = rt.run_cpu(road_hazard_screening, **inputs)

# Embree
rows = rt.run_embree(road_hazard_screening, **inputs)

# OptiX
rows = rt.run_optix(road_hazard_screening, **inputs)
```

## Current Limits
*   **Computational Geometry:** RTDL does not yet claim exact computational geometry; precision is currently "float_approx" (float32).
*   **Vulkan Performance:** While hardware-validated, the Vulkan backend remains slower than OptiX and Embree for large-scale spatial joins.
*   **Overlay Maturity:** The `overlay` workload is currently limited to seed generation; it does not yet perform full polygon fragment materialization.
*   **Hardware Access:** Native AMD and Intel GPU backends are explicitly deferred until hardware-specific validation is possible.
*   **Optimizer:** A generalized multi-backend optimizer is still in development; some workloads may require manual fast-path selection.
