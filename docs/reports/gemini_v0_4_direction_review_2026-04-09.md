# Gemini v0.4 Direction Review

## Verdict

The recommended path (Proposal C: Workload-language-first) is the correct strategic choice, but it is **dangerously close to a semantic shell game**. Turning a 3D demo into a "3D geometric-query workload" only works if there is a credible non-graphical user for those queries. Without a concrete, non-visual 3D application (e.g., 3D spatial join or volumetric collision auditing), `v0.4` risks being perceived as a failed graphics engine hiding behind research terminology.

## Findings

1. **Strongest Objection: The "Identity Slop" Risk.** The move to "bounded 3D query surface" (like `ray_tri_hitcount`) is a pivot toward the most crowded engineering space on earth: ray-tracing for visibility. In this space, RTDL is a toy compared to specialized engines. The project's unique value is its identity as a **spatial database core**. If 3D support does not immediately enable a 3D version of `RayJoin` or a similarly heavy data-processing workload, it is a distraction from the project's primary "non-graphical" mandate.
2. **Backend Maturity Debt.** The `v0.2.0` Jaccard line still relies on native CPU/oracle fallback for public visibility on `optix` and `vulkan`. Promoting a 3D surface to "first-class" status before the 2D surface is natively closed across all backends risks turning RTDL into a "broad but shallow" wrapper rather than a high-performance runtime.
3. **The "Spectacle vs. Substance" Trap.** `v0.3.0` succeeded because the demo was an "attention hook." If `v0.4` fails to deliver a 3D workload that is as performance-competitive against a 3D baseline (like a 3D R-tree or Octree) as `v0.1` was against PostGIS, the project will lose its "performance-first" research credibility.

## Summary

The v0.4 direction is the right one because it forces the project to "put up or shut up" regarding its 3D engineering. To succeed, `v0.4` must move past generic "hit counting" and deliver a **3D spatial-data workload** that solves a problem PostGIS or standard spatial libraries cannot. The "hidden-star" demo must be demoted to a background test case, and the "killer app" for `v0.4` must be a high-row-count 3D geometric join or volumetric analysis tool.
