# Goal 119: Segment/Polygon Native-Maturity Redesign

Date: 2026-04-06
Status: in_progress

## Purpose

Turn the remaining technical gap for `segment_polygon_hitcount` into one clear
implementation target.

The family is already closed for:

- semantics
- correctness
- docs/examples
- large PostGIS validation
- backend audit

What is not yet closed is native backend maturity.

This goal should define the redesign path needed to move the family beyond the
current `native_loop` / correctness-fallback boundary.

## Problem statement

Current accepted status:

- lowering still reports `accel_kind="native_loop"`
- Embree currently uses exact host-side nested loops
- OptiX currently uses exact host-side nested loops
- Vulkan currently uses exact host-side nested loops in native code and the
  public runtime falls back to the native CPU oracle for correctness

So the family is a real feature, but not yet a real RT-backed workload story.

## Required outcomes

1. document the exact current native-maturity gap backend by backend
2. produce one feasibility-tested redesign direction that could move the family
   toward real traversal support
3. define the semantic requirements that the redesign must preserve:
   - boundary-touch counts as hit
   - inside counts as hit
   - each polygon counts once per segment
   - zero-hit segments remain in output
4. define explicit acceptance criteria for a future implementation goal

## Accepted honesty boundary

This goal may recommend a redesign path, but it must not pretend the redesign
is already implemented.

If the current best conclusion is that only one backend looks realistically
promotable in the near term, the report must say that directly.

## Accepted package shape

- one redesign report
- one backend gap matrix
- one recommended next implementation goal with concrete acceptance criteria
