# Goal 110 v0.2 Workload Family Selection

Date: 2026-04-05
Author: Codex
Status: proposed

## Decision

Goal 110 should target:

- `segment_polygon_hitcount`

as the first workload-family closure for RTDL v0.2.

## Direct comparison against `lsi`

`lsi` is important and remains the strongest challenger. The reason not to pick
it first is not presentation optics alone. It is this technical tradeoff:

- `lsi` has richer RT identity, but also:
  - float-valued intersection outputs
  - broader parity history
  - broader scalability baggage from the v0.1 RayJoin-heavy slice
- `segment_polygon_hitcount` has a narrower workload shape, but also:
  - exact integer outputs
  - cleaner correctness comparison
  - a smaller semantic surface to close honestly
  - enough geometric interaction to still count as real spatial filter/refine

So `lsi` is the stronger long-term systems workload, but
`segment_polygon_hitcount` is the better first v0.2 closure target because it
creates a second serious workload story without immediately reopening the most
fragile parts of the v0.1 history.

## Why not `point_nearest_segment`

`point_nearest_segment` is plausible, but it is a weaker flagship than
`segment_polygon_hitcount` because:

- nearest-distance semantics carry tie and near-tie ambiguity
- current local evidence is weaker
- it is easier for the family to look like a convenience closure rather than a
  strong second workload story

So `point_nearest_segment` remains a valid secondary family, but not the best
first closure target.

## Why `segment_polygon_hitcount` fits the charter

The Goal 108 charter requires:

1. candidate generation plus refine/aggregation structure
2. RT candidate search central to the workload
3. plausible backend story on current hardware
4. realistic correctness boundary
5. clear language/runtime value

`segment_polygon_hitcount` satisfies these well:

- segment/polygon candidate filtering is still a natural RTDL shape
- refine semantics are easy to explain:
  - count how many polygons each segment hits
- correctness is realistic:
  - exact row identity
  - exact integer counts
- current code already exposes this workload in:
  - API
  - reference runtime
  - oracle runtime
  - Embree runtime
  - OptiX runtime
  - Vulkan runtime

## What Goal 110 should prove

Goal 110 should prove that RTDL can support a second serious workload family
that is:

- not just another PIP/overlay variant
- not just a novelty demo
- still clearly within RTDL’s non-graphical RT identity

It should not claim more than the evidence allows. If the resulting family
closure still depends on the audited `native_loop` local contract, then the
proof is:

- semantic closure
- backend closure
- user-facing closure

not automatic proof of RT-backed maturity.

## Recommended execution shape

First close correctness and user-facing shape on:

- authored minimal case
- deterministic fixture-backed case
- deterministic derived case beyond the basic fixture

Then, only if the closure is stable, add:

- limited performance notes

Prepared-path checks are part of the Goal 110 acceptance boundary and should be
treated as required, not optional.

Performance should support the workload closure, not redefine it.
