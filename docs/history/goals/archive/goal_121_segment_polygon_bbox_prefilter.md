# Goal 121: Segment-Polygon BBox Prefilter Attempt

Date: 2026-04-06
Status: accepted

## Goal

Try one algorithmic improvement for `segment_polygon_hitcount` that does not
depend on RT cores:

- reject segment/polygon pairs whose axis-aligned bounding boxes do not overlap
  before exact hit testing

This goal exists because Goal 120 showed that moving OptiX onto a native custom
AABB traversal path did not materially improve the large-row timings. The next
question is therefore:

- can a simple candidate-reduction change improve the exact counting paths even
  before a stronger RT-backed redesign exists?

## Implementation surface

The prefilter is applied in:

- Python reference
- native CPU oracle
- Embree exact counting path
- Vulkan exact counting path

The semantics stay unchanged:

- endpoint inside counts as a hit
- boundary touch counts as a hit
- edge crossing counts as a hit
- each polygon counts at most once per segment

## Acceptance rule

This goal succeeds if all of the following hold:

1. correctness stays clean on the accepted closure and PostGIS validation rows
2. the change remains semantically transparent
3. the repo records the real performance result, even if it is weak

This goal does **not** require a competitive result against PostGIS.

## Outcome

The prefilter is now in the code and correctness stayed clean, but the large-row
story changed only slightly:

- small audited rows improved somewhat
- the main large deterministic rows did not materially improve

So Goal 121 closes as:

- a successful bounded algorithmic attempt
- not a decisive performance fix

## Final conclusion

The remaining problem is now sharper:

- the workload is still doing too much exact work after candidate generation

So the next serious performance step, if taken, should be a stronger
candidate-generation / aggregation redesign rather than another small local
prefilter pass.
