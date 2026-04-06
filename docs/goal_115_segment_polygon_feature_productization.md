# Goal 115: Segment-Polygon Feature Productization

Date: 2026-04-05
Status: accepted

## Goal

Turn `segment_polygon_hitcount` from a goal-report-backed feature into a clearly
discoverable and runnable user-facing RTDL capability.

## Why this goal now

After Goals 110, 112, and 114, the family now has:

- workload closure
- performance characterization
- large-scale PostGIS-backed correctness evidence

The next gap is product surface:

- examples should expose the larger deterministic cases directly
- docs should say what the feature now supports
- users should not need to reconstruct the story from multiple goal reports

## Scope

- improve user-facing example ergonomics
- update RTDL docs so the family’s current strength is visible
- make the PostGIS-backed validation path discoverable from the docs

Out of scope:

- changing the family’s architectural honesty boundary
- new backend work
- new workload semantics
