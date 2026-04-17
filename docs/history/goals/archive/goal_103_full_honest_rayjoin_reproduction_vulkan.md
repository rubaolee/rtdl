# Goal 103: Full Honest RayJoin Reproduction, Vulkan-Only

## Objective

Redo the RayJoin-facing reproduction package using only:

- RTDL + Vulkan

with PostGIS retained only as the comparison baseline where that comparison is
valid.

This goal is intentionally honest and bounded. It is not a paper-identical
reproduction claim.

## Scope

Included execution backend:

- RTDL + Vulkan

Comparison baseline where appropriate:

- PostGIS

Excluded from the main execution matrix:

- Embree
- OptiX
- Python oracle
- native C oracle

Those excluded systems may still be mentioned as prior context, but they are
not part of the Goal 103 execution claim.

## Main rule

Every RayJoin paper surface considered for this Vulkan-only package must be
classified explicitly as one of:

- `exact`
- `bounded_analogue`
- `unavailable`
- `not_applicable`

No row may be silently omitted.

## Acceptance

Goal 103 is done when:

- the Vulkan-only RayJoin-facing matrix is frozen
- every row is classified honestly
- all available Vulkan rows are either freshly rerun or carried forward
  explicitly
- unavailable rows are documented with reasons
- the final package states clearly:
  - what is exact
  - what is bounded
  - what is unavailable
  - what is not applicable
- the package receives 2+ AI review before publish
