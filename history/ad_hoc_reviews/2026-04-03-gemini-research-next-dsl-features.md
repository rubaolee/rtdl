# Gemini Research: Next DSL Features Beyond v0.1

Date: 2026-04-03
Model: `gemini-2.5-pro`

Prompt scope:

- RTDL after the current bounded v0.1 RayJoin slice
- identify the next high-value DSL features and workload families
- prioritize features that fit non-graphical ray-tracing execution well

## Summary

Gemini recommended pushing RTDL beyond intersection-style spatial joins toward
workloads that still map cleanly onto traversal hardware and backend-agnostic
execution. The strongest next directions were generalized proximity queries,
point-cloud processing, wave propagation, volumetric analysis, and longer-term
robust geometric operations.

## Recommended workload families and feature directions

1. **DSL Core Enhancements**
   - stronger precision support than the current `float_approx`-style surface
   - richer payload and attribute handling for more complex workloads
   - high leverage because it improves nearly every future workload family

2. **Generalized Proximity Queries**
   - k-nearest-neighbor and radius-search style queries
   - good fit for BVH traversal and closest-hit style execution
   - natural next step after intersection-style joins

3. **Direct Point Cloud Processing**
   - point primitives for LiDAR and photogrammetry workloads
   - avoids forced meshing and expands RTDL beyond polygon-centric data
   - good fit for user-defined primitive support in RT APIs

4. **Wave Propagation and Field Simulation**
   - acoustic, RF, and line-of-sight propagation workloads
   - requires recursive or multi-step ray generation
   - strong non-graphical ray-tracing use case

5. **Volumetric Data Analysis**
   - gridded scalar fields, medical imaging, and simulation volumes
   - enables ray marching, sampling, and iso-surface style workloads
   - more complex than joins, but still within RTDL’s thesis

6. **Advanced Geometric Operations**
   - robust clipping, union, difference, and related operations
   - strategically important, but not as natural a fit to the pure RT model
   - should follow the simpler high-fit workload families above

## Gemini recommended implementation order

1. DSL core enhancements
2. Generalized proximity queries
3. Direct point cloud processing
4. Wave propagation and recursive queries
5. Volumetric data analysis
6. Advanced geometric operations

## Rationale

- **Best architectural fit:** proximity, point-cloud, and wave-propagation
  workloads align cleanly with BVH traversal and backend execution models.
- **Best leverage:** DSL precision and payload improvements raise the ceiling for
  every later workload family.
- **Harder longer-term target:** robust constructive geometry and fully exact
  geometric operations are valuable, but likely require more compiler/runtime
  sophistication and should not be the immediate next step.

## Codex note

This memo is preserved as research input, not as an adopted roadmap. It is
useful for deciding where RTDL should go after the bounded v0.1 RayJoin slice
is closed.
