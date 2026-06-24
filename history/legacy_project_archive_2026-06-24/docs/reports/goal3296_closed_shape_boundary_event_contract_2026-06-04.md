# Goal3296 Closed-Shape Boundary-Event Contract Slice

Date: 2026-06-04

Status: local contract slice, not native OptiX implementation.

## Purpose

Goal3295 showed that the remaining RayJoin-style PIP gap is not row
materialization or host exact-refinement overhead. The tuned Goal3294 path has:

- `candidate_write_pass = 0.0`
- `candidate_download = 0.0`
- `exact_refine = 0.0`

The remaining gap is a contract mismatch. The current RTDL primitive answers
prepared point/closed-shape membership counts, while the faster RayJoin path
selects a representative boundary event along one point ray and leaves later
classification to caller code.

This goal creates the generic RTDL contract target for that shape before adding
native code.

## What Changed

Added a CPU reference oracle:

- `rt.point_closed_shape_first_boundary_crossing_2d_cpu(points, shapes, ...)`

The oracle emits one deterministic event per point/shape pair when a
non-colinear crossing exists:

- `point_id`
- `shape_id`
- `boundary_id`
- `crossing_t`
- `crossing_x`
- `crossing_y`
- `event_kind`

Tie-break policy:

1. smallest non-negative `crossing_t`
2. then smallest `boundary_id`

Added a v2.8 typed geometry relation schema:

- schema: `point_closed_shape_boundary_event_2d_columns`
- producer primitive: `point_closed_shape_first_boundary_crossing_2d`

Added primitive discovery metadata:

- node: `rows.point_closed_shape_boundary_event_columns`
- status: `candidate_behavior`
- backends: `cpu_python_reference`, `planned_optix`

Added an advisory composition recipe:

- `recipe.point_closed_shape_boundary_event_selection`

The recipe composes:

1. `traversal.closest_hit`
2. `rows.point_closed_shape_boundary_event_columns`

## Boundary

No native OptiX ABI was added in this goal.

No app-specific native logic was added.

RayJoin-specific native logic added: false.

The contract emits generic boundary-event columns only. Shape membership
classification, map/entity lookup, parity rules, and paper-system semantics
remain caller-owned.

This goal does not authorize release.

This goal does not authorize public speedup wording.

This goal does not authorize RT-core speedup wording.

This goal does not authorize true-zero-copy wording.

This goal does not claim RayJoin paper reproduction.

## Why This Is The Right Next Slice

The older prepared closed-shape membership primitive is still useful, but it is
too coarse for the fast PIP boundary-selection path. It can answer "how many
point/shape memberships are positive," but it cannot expose the selected
boundary event that a caller might need for custom classification.

The new contract keeps the native engine app-agnostic by naming only generic
geometry concepts:

- point
- closed shape
- boundary id
- crossing parameter
- crossing coordinates
- event kind

It deliberately does not name maps, roads, closest edge IDs, join systems, or
paper-specific workloads.

## Next Engineering Step

The next native slice should implement an OptiX producer for the same schema:

- prepared closed-shape edge/range traversal
- one selected event per point/shape or per point according to an explicit
  contract knob
- typed boundary-event columns resident long enough for caller-selected
  continuation
- parity against `point_closed_shape_first_boundary_crossing_2d_cpu`
- no app-specific native ABI names

That native goal should be pod-validated against the Goal3294/Goal3295
RayJoin same-slice harness, but it should still avoid claiming release
readiness or RayJoin reproduction without external review.
