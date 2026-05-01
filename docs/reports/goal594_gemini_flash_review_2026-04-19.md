# Goal594: Gemini Flash Review of v0.9.2 Apple RT Performance Plan

Date: 2026-04-19

## Planning Verdict: ACCEPT

I accept the proposed v0.9.2 Apple RT performance plan. The approach directly targets the most significant structural inefficiencies (repeated acceleration structure builds per dispatch) while maintaining a strict correctness gate and realistic non-goals.

## Concrete Risks & Recommendations

1. **Precision and Double-Counting in Iterative Nearest-Hit Traversal (Goal597)**
   * **Risk:** Using iterative nearest-hit intersections to implement hit-count by advancing `minDistance` introduces a floating-point precision risk. If the ray's origin or `minDistance` isn't advanced sufficiently, it might re-intersect the same primitive or get stuck in an infinite loop. If advanced too much, it might skip tightly packed, co-planar, or very close triangles.
   * **Recommendation:** Ensure rigorous parity tests against the CPU reference using edge-case geometry (e.g., stacked triangles, very small triangles, intersecting triangles). Implement a deterministic epsilon advancement strategy, and track hit primitive IDs within the traversal loop to prevent double-counting if necessary. Ensure a hard cap is placed on iteration counts to prevent hangs.

2. **Apple MPS `Any` Mode Limitations for All-Hit (Goal598)**
   * **Risk:** As noted, MPS `Any` intersection mode does not provide primitive IDs, requiring reliance on nearest-hit loops for all-pair outputs. In scenarios with high depth complexity (dense geometry), iterative nearest-hit could become performance-prohibitive due to the overhead of launching many consecutive dispatches per ray.
   * **Recommendation:** Timebox the nearest-hit all-pair investigation. If the iterative approach proves too slow for dense scenes compared to a compute-based solution, quickly pivot to the written technical stop and document the limitation. Do not block the overall v0.9.2 release on achieving high performance for segment intersection if MPS lacks the necessary hardware/API support for efficient all-hit enumeration.

3. **Performance Harness Environment Consistency (Goal595)**
   * **Risk:** The performance harness might yield noisy results due to OS-level thermal throttling, CPU/GPU frequency scaling, or background processes on the M4 host.
   * **Recommendation:** Ensure the harness includes sufficient warmup passes before measuring. Record comprehensive statistical metrics (min, median, max, standard deviation) rather than just a single median time to better understand variance.

## Conclusion

The plan is well-scoped and correctly identifies that establishing repeatable measurements and removing redundant AS builds are the critical next steps for the Apple RT backend. Proceed with Goal595 as the first execution step.