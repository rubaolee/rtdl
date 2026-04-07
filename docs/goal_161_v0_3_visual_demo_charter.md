# Goal 161: v0.3 Visual Demo Charter

## Why

After the `v0.2.0` release, the highest-value next direction is a user-facing
demo that is immediately understandable and visually attractive.

The target is a real image/video-style program where:

- RTDL owns the heavy geometric query work
- Python owns scene setup, animation, shading, and media output

This is important because the current small ASCII lit-ball demo proves the
RTDL-plus-Python integration model, but it does not yet make RTDL the dominant
runtime component or produce a compelling visual artifact.

Important lift:

- the current checked-in demo is a **2D** lit-ball slice
- the v0.3 target described here is a **3D** spinning-ball visual demo
- so this is not just "add animation" to the current demo
- it is a real query-surface and geometry-model expansion

## Goal

Define the first v0.3 goal line as:

- a real RTDL-heavy visual demo package

with a first concrete target:

- a spinning triangulated ball
- two or more orbiting lights
- real image frames and/or a short clip
- visually rich brightness/color changes over time

## Core Architectural Boundary

This goal is **not** a claim that RTDL is becoming a general rendering engine.

The intended model is:

- RTDL:
  - ray/triangle relationship work
  - dense geometric query work per frame
  - the dominant heavy query surface
- Python:
  - scene construction
  - animation loop
  - light motion
  - shading math
  - image/video writing

## Scope

The charter must answer:

1. what minimum RTDL query surface is needed for a compelling visual demo
2. whether the current `ray_tri_hitcount` line is enough
3. whether a new nearest-hit or hit-row workload is required
4. how the current 2D demo should be lifted into a 3D visual-demo path
5. how to stage the work into:
   - kernel/runtime work
   - demo construction
   - correctness/testing
   - media artifact generation

## Success Criteria

The v0.3 visual-demo line should aim to produce:

- a checked-in demo program
- real non-ASCII image frames and/or a short clip
- a clear explanation of what RTDL computes versus what Python computes
- a case where RTDL is plausibly the dominant runtime cost
- at least one backend-comparison or correctness check on the accepted demo
  query surface

## Not In Scope

- claiming RTDL is now a full rendering language
- general materials/textures/cameras as a full graphics system
- replacing the non-graphical RTDL identity
- broad open-ended rendering features before a narrow demo is closed

## Acceptance

- the repo has one checked-in v0.3 first-goal charter for the visual-demo line
- the charter explains why this is a good post-`v0.2.0` priority
- the RTDL-vs-Python responsibility split is explicit
- the non-renderer honesty boundary is explicit
- the package has `2+` review coverage with at least one Claude or Gemini
  review before closure
