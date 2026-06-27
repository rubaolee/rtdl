# Gemini Review: Goal 69 PIP Performance Repair Design

Date: 2026-04-04
Model: `gemini-3.1-pro-preview`

Verdict: `APPROVE-WITH-NOTES`

Accepted points:
- adding `result_mode="positive_hits"` is an honest way to compare RTDL against
  the indexed PostGIS positive-hit query shape
- keeping `full_matrix` as the default preserves the accepted Goal 50 baseline
- the action order is sound:
  - API/contract
  - implementation
  - tests
  - harness
  - final review

Main notes from Gemini:
1. Row multiplicity still matters.
   - if a point can match multiple polygons, RTDL must emit the same number of
     positive-hit rows as PostGIS
2. Timing fairness still needs care.
   - PostGIS query timing benefits from an already-built GiST index after load
   - RTDL backend timing may still include BVH build work inside the timed
     execution window

Codex note:
- both points are accepted
- row-count/hash parity remains part of Goal 69
- the BVH-vs-GiST timing boundary must be documented honestly even if it is not
  fully repaired in this goal
