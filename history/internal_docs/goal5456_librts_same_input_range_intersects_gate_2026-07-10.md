# Goal5456 - LibRTS Same-Input Range-Intersects Gate

Date: 2026-07-10

## Objective

Close the third bounded LibRTS query operation with a predicate-discriminating
fixture and public generic RTDL count/row APIs.

## Discriminating Fixture

The same indexed boxes and query boxes produce:

```text
range_contains count = 5
range_intersects count = 8
```

Therefore accidentally invoking contains cannot pass the intersects gate.
Boundary contact is inclusive, matching author `Envelope::Intersects` and RTDL
AABB semantics.

## Live Result

Environment: `lx1 / 192.168.1.20`, GTX 1070, functional evidence only.

```text
author commit match = true
same input hashes = true
author RTSpatial/OptiX range-intersects count = 8
RTDL OptiX range-intersects count = 8
RTDL OptiX native intersection rows = 8
RTDL complete_candidate_coverage = true
RTDL rt_core_accelerated = true
RTDL native_engine_customization = false
matched = true
Embree used = false
```

RTDL native rows:

```text
(0,0), (0,1), (1,0), (1,1),
(2,0), (2,1), (3,2), (4,3)
```

Public APIs:

```text
query_aabb_index_2d(operation="range_intersects")
aabb_intersection_pair_rows_2d
```

The author example remains count-only. Author pair-row agreement is not
claimed; RTDL native row agreement is independently verified against the exact
fixture.

Evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5456_same_input_range_intersects.json
```

## Validation

```text
Goal5456 local tests = 3 OK
Goal5456 Linux tests = 3 OK
Goals5453-5456 consolidated local/portfolio slice = 27 OK
live author/RTDL OptiX gate = matched
```

## Timing Boundary

One author diagnostic is recorded (`load 2.48ms`, `query 0.345ms`). There is no
matched RTDL phase timing and no authorized ratio. GTX 1070 is not paper
performance evidence.

## Query-Surface Milestone

The first bounded LibRTS query milestone is now implemented:

```text
point_contains:    author count 5 == RTDL count 5; RTDL exact rows 5
range_contains:    author count 5 == RTDL count 5; direction 5 vs reverse 2
range_intersects:  author count 8 == RTDL count 8; RTDL native rows 8
```

This is a same-input query-surface correctness result, not full paper
reproduction and not performance parity.

## Next Goal

Before implementing mutations, Goal5457 should audit the mismatch between
LibRTS's mutable `Insert/Update/Delete/Clear` lifecycle and RTDL's current
prepared AABB APIs. It must decide whether existing generic rebuild semantics
are sufficient or a new app-neutral mutable prepared-index contract is needed.
No mutation code should be added until that audit names a non-LibRTS consumer.

## Exit Label

```text
goal5456_librts_bounded_same_input_query_surface_complete__review_pending
```
