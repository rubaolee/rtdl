# Goal 119 Segment/Polygon Native-Maturity Redesign

Date: 2026-04-06
Status: current redesign package

## Summary

`segment_polygon_hitcount` is now a real RTDL feature, but it is still not a
native RT-backed workload family.

The current backend reality is:

- lowering still marks the family as `native_loop`
- Embree computes counts with exact host-side nested loops
- OptiX computes counts with exact host-side nested loops
- Vulkan computes counts with exact host-side nested loops in native code and
  the public runtime still falls back to the native CPU oracle

So the feature is finished at the product/correctness level, but not at the
native backend maturity level.

This report turns that fact into one concrete redesign target rather than
leaving it as vague “future optimization.”

## What The Workload Really Needs

For each segment, emit exactly one row:

- `segment_id`
- `hit_count`

Where a polygon contributes `1` to the count if any of the following is true:

- the segment crosses a polygon edge
- an endpoint touches the polygon boundary
- the segment lies inside the polygon

And two constraints must remain true:

- each polygon counts at most once per segment
- zero-hit segments still appear in output

That means this workload is not just primitive hit detection.
It is:

- candidate generation
- exact segment-vs-polygon refinement
- polygon deduplication
- count aggregation

## Current Backend Gap Matrix

| Layer | Current status | Main gap |
| --- | --- | --- |
| lowering | `native_loop` | no accepted BVH/traversal plan yet |
| CPU oracle | accepted | not a performance target |
| Embree | exact nested loops | no scene/traversal use for this family |
| OptiX | exact nested loops | no device candidate traversal for this family |
| Vulkan native code | exact nested loops | no native accelerated path |
| Vulkan public runtime | CPU fallback | correctness is protected, but not native |

The important point is that all three non-oracle backends still share the same
structural weakness:

- no accepted candidate-traversal stage

## Feasible Redesign Direction

The most credible redesign is:

### 1. Build-side acceleration over polygon AABBs

For each polygon:

- compute one conservative AABB
- build an acceleration structure over those polygon AABBs

This avoids counting raw polygon edges as separate hits and gives one candidate
identity per polygon.

### 2. Probe with finite segments as finite rays

For each segment:

- cast it as a finite probe ray
- traverse the polygon-AABB acceleration structure
- collect candidate polygon ids

Candidate generation must be conservative:

- false positives are acceptable
- false negatives are not

### 3. Exact refine per candidate polygon

For each candidate `(segment, polygon)` pair:

- run the exact current segment-vs-polygon predicate
- preserve today’s semantics for:
  - boundary touch
  - inside
  - crossing

### 4. Deduplicate by polygon id

If traversal can see the same polygon more than once, deduplicate before
counting.

The final output remains:

- one row per segment
- one integer hit count

## Why This Is Better Than Edge-Based Traversal

A raw edge-based traversal would create extra complexity:

- one polygon can yield many candidate edges
- dedup becomes mandatory even on simple crossings
- inside-only cases still need a separate containment supplement

A polygon-AABB candidate stage is cleaner because:

- one candidate identity is already polygon-level
- exact refine can remain the current trusted predicate
- aggregation remains simple

## Backend Reading

### OptiX

This is the most realistic near-term promotion target.

Reason:

- OptiX already has mature custom-AABB traversal for other workloads
- the missing piece is not the traversal platform itself
- the missing piece is a parity-safe segment/polygon candidate design

Recommended reading:

- first backend to target for a native redesign attempt

### Embree

Embree is plausible, but less strategically important than OptiX for native
promotion on this family.

Reason:

- current performance is close to CPU
- a redesign would improve structural honesty, but likely not transform the
  performance story

Recommended reading:

- follow OptiX after the design is proven, or keep as a correctness/stability
  fallback if time is limited

### Vulkan

Vulkan is the hardest current promotion target.

Reason:

- current public path still relies on CPU fallback for correctness
- the family would need both:
  - a new candidate traversal design
  - a trustworthy native runtime path

Recommended reading:

- do not make Vulkan the first native-redesign target for this family

## Recommended Next Implementation Goal

The next concrete implementation goal should be:

- **Goal 120: OptiX polygon-AABB candidate traversal for `segment_polygon_hitcount`**

That goal should attempt only one backend-first redesign:

- OptiX first

And it should keep the current exact predicate for final truth.

## Acceptance Criteria For Goal 120

1. lowering no longer needs to describe OptiX as pure `native_loop` for this
   family
2. OptiX candidate generation is conservative on authored, fixture, derived,
   and large deterministic cases
3. final OptiX rows remain parity-clean vs:
   - Python oracle
   - PostGIS on accepted large deterministic rows
4. the final package distinguishes:
   - candidate traversal stage
   - exact refine stage
   - aggregation stage
5. if performance does not improve, the package must still say whether the
   redesign was worth taking for architectural reasons alone

## Final Conclusion

The feature is already finished as a real RTDL feature.

What is unfinished is specifically:

- native backend maturity

The most realistic next step is not broad “backend optimization” in the
abstract. It is:

- one OptiX-first polygon-AABB candidate redesign

That is the clearest path from today’s correct/productized feature toward a
true RT-backed workload story.
