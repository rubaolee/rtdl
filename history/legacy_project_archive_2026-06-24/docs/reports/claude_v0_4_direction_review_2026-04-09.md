## Verdict

The switch is correct. The 3D-first draft would have compounded v0.3's identity drift; nearest-neighbor search fits RTDL's stated lane, has direct research paper support (RTNN, X-HD), and gives v0.4 a workload identity that is meaningfully new without changing what the project claims to be. The direction document makes the right call on all three competing proposals.

---

## Findings

**What holds up:**

- The Proposal A/B/C analysis is honest. Rejecting demo-first and backend-only-first as v0.4 headlines is the right structural move. Both would have produced a release with no new user-facing capability.
- Fixed-radius-first, KNN-second is sound sequencing. Fixed-radius has a simpler row contract and a cleaner correctness story; KNN as Goal 6 avoids the tie-policy and overflow complexity landing at the same time as the initial implementation.
- The warning to keep Hausdorff distance out of v0.4 scope is correct. X-HD depends on nearest-neighbor as a primitive; building the primitive first is the right order.

**What is weak or missing:**

- The external comparison baseline is unresolved. Goal 194 says "brute-force CPU reference" or "existing neighbor-search libraries" but names nothing. PostGIS was a concrete anchor; the nearest-neighbor story has no equivalent yet. This needs a named baseline before the benchmark goal (Goal 8) starts, not during it.
- Goal 194's finish line contains a factual inconsistency: the final sentence asks "how do we implement the first bounded `point_in_volume` workload cleanly?" — but `point_in_volume` is not the v0.4 workload. The milestone is `fixed_radius_neighbors`. This looks like a copy-paste artifact from a different draft and should be corrected before this document is used as a kickoff anchor.
- The backend acceptance plan calls Embree the "first high-confidence native backend" but does not say whether the existing Embree spatial-join kernel infrastructure transfers to nearest-neighbor search or has to be rebuilt. If the AABB/BVH construction for points is different in kind from the segment/polygon surface, that's a real implementation risk that Goals 3 and 4 need to surface early.

---

## Summary

Replace the 3D-first draft. It was the wrong identity for a project whose README leads with "non-graphical geometric-query workloads." The nearest-neighbor package is coherent, research-backed, and properly sequenced. Two things need to be fixed before this becomes a clean kickoff: (1) the finish line sentence must be corrected from `point_in_volume` to `fixed_radius_neighbors`, and (2) a concrete external comparison baseline needs to be named now, not deferred to the benchmark goal.
