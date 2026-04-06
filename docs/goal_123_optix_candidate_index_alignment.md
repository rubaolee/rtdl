# Goal 123: OptiX Candidate-Index Alignment

Date: 2026-04-06
Status: accepted

## Goal

Bring OptiX onto the same candidate-reduction strategy that already improved
the Python reference, native CPU oracle, Embree, and Vulkan paths in Goal 122.

The key move is:

- default OptiX `segment_polygon_hitcount` to the host-indexed candidate path
- keep the older native OptiX traversal path behind an explicit environment
  switch for future experiments

## Why this goal exists

After Goal 122:

- CPU, Embree, and Vulkan improved drastically
- OptiX remained slow

The split happened because OptiX was still on a separate path and therefore did
not benefit from the same candidate-index redesign.

## Intended outcome

This goal succeeds if:

1. OptiX correctness stays clean
2. large deterministic Linux/PostGIS rows stay parity-clean
3. OptiX large deterministic performance materially improves
4. the final package clearly states that the gain comes from alignment with the
   host-indexed candidate strategy, not from a new RT-core-native win

## Final conclusion

Goal 123 closes as a successful performance alignment step:

- OptiX now shares the same candidate-reduction idea as the other backends
- the large deterministic Linux rows improved dramatically
- OptiX now beats PostGIS on the larger audited deterministic rows

The remaining honesty boundary is explicit:

- this is a strong performance win for the feature
- but not a new native RT-core maturity claim

External Claude review was completed afterward in:

- [goal107_123_package_review_claude_2026-04-06.md](reports/goal107_123_package_review_claude_2026-04-06.md)
