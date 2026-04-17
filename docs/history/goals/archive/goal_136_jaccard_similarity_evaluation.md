# Goal 136: Jaccard Similarity Evaluation

## Goal

Evaluate whether RTDL should take on pathology-style polygon-set Jaccard
similarity, inspired by:

- Kaibo Wang et al.,
  *Accelerating Pathology Image Data Cross-Comparison on CPU-GPU Hybrid Systems*,
  PVLDB 2012

and answer these questions:

1. Is this a legitimate RTDL workload direction?
2. If yes, what is the honest scope boundary?
3. What concrete next goals would be required for full implementation,
   testing, PostGIS backing, and public-data closure?
4. If no, why not?

## Required outcomes

- extract the relevant workload meaning from the old paper
- compare it against current RTDL strengths and limits
- make a clear accept/reject recommendation
- if accepted, define a next-goal sequence with:
  - coding
  - testing
  - Linux/PostGIS validation
  - public-data acquisition/conversion
- obtain at least `2+` review/consensus coverage before final acceptance

## Boundary

This goal is about **pathology polygon-set Jaccard**, not generic arbitrary
set-similarity search.
