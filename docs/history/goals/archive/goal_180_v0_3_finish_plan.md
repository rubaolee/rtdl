# Goal 180: v0.3 Finish Plan

## Why

The `v0.3` line is already strong technically, but it is not yet cleanly finished as a public-facing package. The remaining work is no longer about proving that RTDL can participate in 3D demo workloads. It is about closing the remaining flagship-demo and release-surface gaps under the repo's `2+` AI consensus rule.

## Scope

- write an explicit ordered finish plan for the remainder of `v0.3`
- keep the plan bounded to the already-proven visual-demo line
- make the closure sequence explicit for:
  - flagship smooth-camera artifact acceptance
  - Linux supporting backend preview acceptance
  - front-surface/public-artifact selection
  - final `v0.3` status/release-style package
- preserve the RTDL honesty boundary:
  - RTDL remains the geometric-query core
  - Python remains responsible for scene, shading, post-process, and media output
- send the plan through the same review discipline as other goals:
  - external AI review
  - Codex consensus

## Proposed Finish Sequence

### Goal 181: Smooth-Camera Flagship Acceptance

- accept one final Windows Embree smooth-camera movie as the flagship `v0.3` visual artifact
- include:
  - Windows run facts
  - artifact paths
  - known limitations
- explicitly choose between:
  - the current warm-fill smooth-camera movie
  - the newer brighter-white secondary-light variant if it is judged better

### Goal 182: Linux Smooth-Camera Supporting Package

- package the Linux OptiX and Vulkan smooth-camera previews as supporting backend artifacts
- require frame `0` compare-clean parity against `cpu_python_reference`
- keep them explicitly secondary to the Windows Embree flagship movie

### Goal 183: Front Surface and Public Artifact Refresh

- update the repo front surface if the flagship artifact changes
- keep one clear primary public link or artifact recommendation
- keep backend/platform honesty visible

### Goal 184: v0.3 Final Status Package

- write the final `v0.3` closure/status package
- summarize:
  - what RTDL proved
  - what backend/platform support is bounded and real
  - what the flagship demo artifact is
  - what remains future work rather than part of `v0.3`

## Success Criteria

- the remainder of `v0.3` is reduced to a short ordered goal list
- the flagship movie acceptance path is explicit
- the Linux supporting-artifact path is explicit
- the front-surface update path is explicit
- the final `v0.3` package path is explicit
- the plan receives `2+` AI consensus before execution begins

## Out of Scope

- inventing a new unrelated demo concept
- reopening already accepted backend-correctness goals
- claiming final renderer maturity or cinematic perfection
