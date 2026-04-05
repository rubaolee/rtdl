# Goal 102: Full Honest RayJoin Reproduction

## Objective

Reproduce the RayJoin paper experiment surface as fully and honestly as the
current repository, datasets, and hardware allow.

This goal is intentionally narrower than a paper-identical reproduction claim.
It is a **fullest honest reproduction** goal, not an overclaim goal.

## Scope

Included execution backends:

- RTDL + Embree
- RTDL + OptiX

Comparison baseline where appropriate:

- PostGIS

Excluded from the main execution matrix:

- Vulkan
- Python oracle
- native C oracle

Those excluded systems may still be used as correctness references where
needed, but they are not part of the main reproduction-performance claim.

## Main rule

Every RayJoin paper surface must be classified explicitly as one of:

- `exact`
- `bounded_analogue`
- `unavailable`
- `not_applicable`

No row may be silently omitted.

## What this goal must cover

The target surface includes, as far as they are available:

- RayJoin Table 3 style workload families
  - LSI
  - PIP
- RayJoin Figure 13 style LSI scalability
- RayJoin Figure 14 style PIP scalability
- RayJoin Table 4 / Figure 15 style overlay-related surface

For each row, the package must state:

- dataset family
- provenance
- whether the row is exact or bounded
- which backends ran
- which timing boundary is being claimed
- whether PostGIS is a valid comparison row there

## Acceptance

Goal 102 is done when:

- the full RayJoin-facing experiment matrix is frozen
- all available exact or bounded rows have been rerun or carried forward
  honestly
- unavailable rows are documented with explicit reasons
- the final package states clearly:
  - what is exact
  - what is bounded
  - what is unavailable
- Embree and OptiX are the only primary execution backends in the package
- the package receives 2+ AI review before publish
