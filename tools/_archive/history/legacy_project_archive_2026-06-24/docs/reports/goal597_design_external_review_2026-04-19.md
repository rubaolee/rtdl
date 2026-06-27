# Goal 597: External Design Review
Date: 2026-04-19

## Verdict: ACCEPT

## Review Summary
The proposed masked chunked nearest-hit strategy is the right exactness-preserving first candidate for Apple RT hit-count optimization under the MPS API.

### Key Strengths of the Proposal:
1. **Semantic Correctness:** The decision to avoid relying solely on `minDistance` epsilon-advancement is mathematically sound. Co-planar and exactly-same-distance primitives are a common edge case; mask clearing provides a robust mechanism to guarantee zero double-counting while capturing all intersections at identical distances.
2. **MPS API Compatibility:** Since MPS does not guarantee primitive indices for `Any` hit types, the pivot to `Nearest` with a `PrimitiveIndex` is a necessary workaround. Utilizing the 32-bit primitive/ray mask is an elegant application of the API's constraints.
3. **Performance Bound:** The theoretical worst-case performance gracefully degrades to the current single-primitive dispatch bounds, meaning we cap regressions while providing a potential 32x reduction in acceleration-structure builds.

### Recommendations for Implementation:
- **Epsilon Policy Adherence:** Strictly follow the proposed "no distance advancement" rule for correctness. If a defensive epsilon is required for MPS infinite loops, ensure it acts purely as a fallback.
- **Fixture Rigor:** The identified test fixtures are comprehensive. Ensure the >32 triangles test explicitly forces hits across chunk boundaries to validate state carryover.

The masked chunked method is the most credible path to preserve exact CPU-parity hit counting while improving the AS build overhead.
