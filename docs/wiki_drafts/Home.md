# Historical Wiki Draft Note

This page was imported from a parallel checkout on 2026-04-10 as a preserved
draft artifact. It is **not** the current live source of truth for RTDL docs.
For current onboarding, start at [docs/README.md](/Users/rl2025/rtdl_python_only/docs/README.md).

---

# Welcome to the RTDL Wiki

RTDL (Ray Tracing Data Layer) is a high-performance research runtime for **non-graphical geometric-query workloads**. 

While traditional ray tracing is focused on "what does this pixel see?", RTDL repurposes that core traversal machinery to answer spatial data questions at massive scale:
*   Which line segments intersect?
*   Which points fall inside which polygons?
*   How similar are these complex geometric sets? (Jaccard Similarity)

## Key Project Pillars

### 1. Unified Geometric DSL
Write your spatial logic once using the RTDL Python DSL. The system handles the complex lowering to high-performance acceleration structures (BVH) and native backends.

### 2. Native Backend Parity
RTDL provides bit-identical (or epsilon-consistent) results across multiple backends:
*   **Embree**: High-performance CPU ray tracing (native).
*   **OptiX**: GPU-accelerated ray tracing via NVIDIA RTX kernels.
*   **Vulkan**: Cross-vendor GPU acceleration.
*   **Oracle**: Ground-truth reference for validation.

### 3. Python-First Application Layer
RTDL is designed to be the "geometric engine" for Python applications. It handles the heavy lifting of spatial indexing and querying, leaving the user to handle the high-level logic, summaries, and visualization in Python.

---

## Navigation
- [Quick Start](Quick-Start.md)
- [Core Concepts](Core-Concepts.md)
- [Backends](Backends.md)
- [Example Gallery](Example-Gallery.md)
