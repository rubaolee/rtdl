# Codex Consensus: Goal 136 Jaccard Similarity Evaluation

## Verdict

Keep, with the narrowed framing.

## Findings

- The old paper is a valid RTDL-adjacent target because it is about spatial
  polygon-set cross-comparison, not generic arbitrary set similarity.
- The technically correct way into this line is not “Jaccard support” all at
  once. It is:
  - `polygon_pair_overlap_area_rows` first
  - then `polygon_set_jaccard`
- Current RTDL does not already have the needed primitive:
  - `overlay` remains a seed-generation analogue
  - there is no accepted overlap-area primitive today
- Public-data and PostGIS stories are credible:
  - pathology segmentation datasets can be converted into polygons
  - PostGIS can provide an external area/intersection baseline
- The first draft overstated the decision slightly; that has been corrected to:
  - accepted as a narrow possible next direction
  - not yet a guaranteed full family commitment

## Summary

Goal 136 should stand as a decision-and-scope report, not as an implementation
claim. RTDL may pursue pathology polygon-set Jaccard, but only through a narrow
primitive-first path with explicit CPU/Python/PostGIS closure before any broad
backend or product claims.
