# Goal2481 Consensus: Robot Collision Generic Contract

Date: 2026-05-21

## Consensus: Approved

Codex, Gemini, and Claude agree that Goal2481 can close and that Goal2482 may
proceed under the reviewed contract.

## Contract Approved

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

Shape:

```text
prepared_static_triangle_scene_3d
+ grouped finite 3D query segment probes
-> byte-per-query-group uint8 any-hit flags
```

## Review Verdicts

Gemini:

- Verdict: Approved.
- Blocking issues: none.
- Assessment: the contract is concrete, app-agnostic, defensible for Embree and
  OptiX, and the `uint8` output format is appropriate for V1.

Claude:

- Verdict: Approved.
- Blocking issues: none.
- Assessment: agreed with Gemini and accepted the contract as minimal and
  implementable.
- Non-blocking refinements: clarify zero-length segment enforcement, clarify
  query-coordinate precision narrowing, and state that Goal2481 tests/reviews
  must be green before Goal2482 native work begins.

## Accepted Refinements

- Zero-length query segments are invalid and must be rejected by the Python
  packer before native traversal.
- Static scene and query segment coordinates may both be narrowed by a backend
  only if metadata records the narrowing.
- Goal2482 must include at least one full-float64 input fixture to surface
  precision narrowing issues.
- Goal2481 tests, external reviews, and this consensus artifact must be green
  before native Embree work begins.

## Boundary Confirmed

The native engine must not know application concepts. Active Embree/OptiX native
code is guarded against these words for this lane:

```text
robot, link, pose, joint, kinematic, kinematics, planner, collision
```

Python remains responsible for application geometry, transforms, grouping,
interpretation, exact fallback policy, and paper-specific meaning.

## Goal2482 Authorization

Goal2482 may proceed only as an Embree implementation of the approved generic
contract. It must not add native robot-collision, exact solid-collision,
continuous-collision, row-witness, or public performance-claim scope.
