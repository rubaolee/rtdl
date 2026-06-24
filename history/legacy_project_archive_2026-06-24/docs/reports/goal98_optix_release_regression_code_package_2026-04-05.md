# Goal 98 Code Package: OptiX Release Regression Repair

Date: 2026-04-05
Status: ready for review

## Scope

This code package contains the minimal OptiX repair needed to address the clean
release-clone positive-hit prepared regression on the exact-source long
`county_zipcode` surface.

Changed file:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`

## Code changes

1. Positive-hit OptiX candidate generation is now conservative by design.

In `__intersection__pip_isect`, when `params.positive_only != 0u`:

- the kernel reports every AABB candidate
- it does **not** run the float32 GPU `point_in_polygon(...)` truth test first

That means:

- host exact finalize now sees all plausible positive-hit candidates
- float32 GPU false negatives can no longer silently drop true rows before
  finalize

2. Polygon broad-phase tolerance is slightly widened.

- `kAabbPad` was increased
- the float32 `point_eps` comment was clarified as non-positive-only only

This is secondary support, not the decisive fix.

3. Redundant positive-only launch-param re-upload was removed.

- the shared output counter reset remains
- the unchanged param-buffer re-upload was dropped

## Intended effect

The repaired code should restore:

- exact parity on the clean-clone OptiX prepared exact-source positive-hit
  surface
- exact parity on the clean-clone OptiX repeated raw-input exact-source
  surface

The accepted OptiX claim boundary remains:

- prepared warmed rerun win, not unconditional cold first-run prepared win
- repeated raw-input exact-source win with parity preserved

## Non-goals

- no broad OptiX refactor
- no full-matrix PIP claim change
- no Embree/Vulkan code changes
