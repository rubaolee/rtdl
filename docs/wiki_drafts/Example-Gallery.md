# Historical Wiki Draft Note

This page was imported from a parallel checkout on 2026-04-10 as a preserved
draft artifact. It is **not** the current live source of truth for RTDL docs.
For current examples, start at [examples/README.md](../../examples/README.md)
and [docs/release_facing_examples.md](../release_facing_examples.md).

---

# Example Gallery

The RTDL repository includes several classes of examples, ranging from tiny "Hello World" programs to complex 3D visual demonstrations.

## 1. Reference Kernels
Located in `examples/reference/`, these kernels represent the "Canonical" geometric query workloads.

*   **Hit Counting**: `rtdl_segment_polygon_hitcount.py` - Counts how many times a set of segments pierces each polygon.
*   **Any-Hit Emission**: `rtdl_segment_polygon_anyhit_rows.py` - Emits a record for every single intersection found between segments and polygons.
*   **Jaccard Similarity**: `rtdl_polygon_set_jaccard.py` - Computes the geometric similarity between two sets of polygons by measuring intersection vs. union.
*   **Road Hazard Screening**: `rtdl_road_hazard_screening.py` - A realistic scenario demonstrating how a search radius can be used to screen for hazards around road segments.

## 2. Visual Demos (v0.3)
Located in `examples/visual_demo/`, these applications demonstrate that RTDL's query core is fast enough to drive real-time visual output.

*   **Earth "Flying Star" Demo**: `rtdl_earth_flying_star_demo.py` - A high-fidelity demo featuring a procedurally shaded Earth, shadows, and a dynamic 3D light source ("The Flying Star").
*   **Spinning Ball**: `rtdl_spinning_ball_3d_demo.py` - The foundational 3D demo showing smooth sphere/ray intersection and shading.
*   **Smooth Camera Orbit**: `rtdl_smooth_camera_orbit_demo.py` - Demonstrates camera pathing and viewpoint transitions using RTDL's query core.

## 3. Tooling & Bundles
*   **Handoff Bundles**: `examples/rtdl_generated_segment_polygon_bundle/` - Demonstrates how RTDL can generate "Generate-Only" bundles for use in environments without a full RTDL runtime.

---

## Running the Examples
Most examples take a `--backend` argument. To see the speed difference between Python and Native backends, try:

```bash
# Slow Python Reference
PYTHONPATH=src:. python3 examples/reference/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference

# Fast Native Embree
PYTHONPATH=src:. python3 examples/reference/rtdl_segment_polygon_hitcount.py --backend embree
```
