# Goal 120: OptiX Segment/Polygon Native Promotion

Date: 2026-04-06
Status: accepted

## Purpose

Take the first implementation step beyond the `native_loop` boundary for
`segment_polygon_hitcount`, starting with OptiX.

This goal does not require a final full-backend redesign. It requires one real
backend-first promotion attempt and an honest read on whether that attempt
actually helps.

## Required outcomes

1. the OptiX runtime no longer uses exact host-side nested loops for this
   family
2. parity remains clean on the accepted closure cases
3. large deterministic PostGIS parity remains clean on Linux
4. the final package states clearly whether the native promotion attempt
   produced a meaningful speedup

## Accepted honesty boundary

If the implementation changes the architecture but does not materially improve
performance, the final report must say that directly.

This goal may close as:

- architectural/native promotion success
- but not performance success

if that is what the evidence shows.
