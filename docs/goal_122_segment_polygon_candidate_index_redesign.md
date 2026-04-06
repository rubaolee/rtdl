# Goal 122: Segment-Polygon Candidate-Index Redesign

Date: 2026-04-06
Status: pending external Claude review

## Goal

Turn the bounded bbox-prefilter improvement from Goal 121 into a stronger
candidate-reduction redesign that can materially change the large-row Linux
performance story for `segment_polygon_hitcount`.

The key idea is:

- do not linearly scan all polygons per segment, even with cheap bbox checks
- instead, build a simple polygon candidate index over bbox x-ranges and only
  visit nearby polygons for each segment

## Why this goal exists

Goal 121 showed:

- exact work could be reduced a little
- correctness stayed clean
- but the large deterministic rows still did not materially improve

That meant the remaining problem was not only exact predicate cost. It was also:

- candidate scanning cost

## Chosen redesign

For the current exact counting paths, build a 1D bucket index over polygon
bounding boxes:

1. compute polygon bboxes
2. bucket polygons by x-range overlap
3. for each segment bbox, visit only polygons in overlapping buckets
4. deduplicate polygon candidates
5. keep the exact refine semantics unchanged

This redesign is intentionally simple:

- it does not change the semantic contract
- it does not require RT cores
- it can help Python/native CPU, Embree, and Vulkan immediately

## Outcome

The redesign is now implemented in:

- Python reference
- native CPU oracle
- Embree exact counting path
- Vulkan exact counting path

Correctness stayed clean, and the large deterministic Linux rows changed
materially for CPU, Embree, and Vulkan.

OptiX did **not** materially improve, because its current path does not use this
host-side candidate index.

## Final conclusion

Goal 122 closes as a real algorithmic win for this feature family:

- CPU/Embree/Vulkan now have a materially stronger performance story
- OptiX remains the clear remaining redesign target

Because the user requested Claude as part of the consensus flow and that review
is not available in this tool environment, the package is marked:

- pending external Claude review
