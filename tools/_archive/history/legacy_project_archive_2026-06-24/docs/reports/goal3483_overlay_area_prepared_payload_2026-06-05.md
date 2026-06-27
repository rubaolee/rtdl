# Goal3483 - Overlay-Area Prepared Payload Prototype

## Status

Implemented locally.

Goal3483 moves the v2.8 spatial RayJoin overlay-area path one step closer to a
runtime kernel without writing the kernel yet. Goal3482 defined the pre-kernel
policy; this goal defines a CPU prototype for the prepared simple polygon
component payload. In stricter contract wording, this is the `prepared simple polygon component payload`
that a future scalar exact-area device continuation should consume.

## What Changed

New module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

The module adds:

- `prepare_simple_polygon_component_payload(...)`
- `prepare_overlay_area_pair_rows(...)`
- `evaluate_prepared_overlay_area_scalar(...)`
- `validate_v2_8_overlay_area_prepared_payload_contract()`

The payload converts already-canonical simple polygon components into triangle
ranges:

- one flat triangle array;
- one component table with source ids, triangle start/count, and vertex count;
- one row-pair table with left/right component ordinals and triangle ranges.

The evaluator computes scalar exact area over those prepared rows by summing
triangle-pair convex clipping. This is a CPU prototype and reference shape for
the future bounded/tiled device continuation.

## Boundary

The payload intentionally does not repair raw topology. Invalid,
self-intersecting, degenerate, hole-bearing, or otherwise non-prepared inputs
must be canonicalized before this layer. Unsupported inputs fail closed with:

- `unsupported_topology_not_canonicalized`

In short, unsupported topology fails closed. This goal does not authorize a runtime kernel, public speedup wording, RT-core
speedup wording, true-zero-copy wording, release packaging, hidden dispatch,
automatic partner selection, paper reproduction claims, or app-specific native
engine behavior.

## Fixture Evidence

The validation fixture uses:

- left component: a concave L-shaped simple polygon;
- right component: an overlapping square.

Expected prepared shape:

- left triangles: `4`;
- right triangles: `2`;
- triangle pairs: `8`;
- scalar exact area: `1.75`.

The prepared-payload evaluator matches the Goal3481 reference algorithm on that
fixture.

## Why This Matters

Goal3477 showed that full overlay geometry can produce large component/vertex
streams, but the near-term benchmark target can stay scalar exact area first.
For scalar area, the future GPU path should not materialize output geometry and
should not consume raw topology. It should consume prepared component triangles,
row ownership, and bounded triangle-pair tiles.

This goal gives that future kernel a precise, generic input shape.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3483_overlay_area_prepared_payload_test`
- `py -3 -m unittest tests.goal3482_overlay_area_pre_kernel_policy_test`
- `py -3 -m unittest tests.goal3481_simple_polygon_overlay_area_reference_algorithm_test`
