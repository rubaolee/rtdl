# Goal1971 Gemini Review for Goal1969 CuPy Extent Polygon Candidate Backend

**Date:** 2026-05-14

**Verdict:** `accept-with-boundary`

## Review Summary

Goal1969 introduces a `cupy_extent` candidate backend for polygon overlap calculations, specifically addressing a performance bottleneck in candidate construction identified in Goal1968. The implementation leverages CuPy tensor operations and a CuPy RawKernel to efficiently compute overlapping 2D extent candidates. The solution demonstrates significant performance improvements for the targeted polygon control rows compared to both `cpu_all_pairs` and Embree candidate discovery, while maintaining correctness against the v1.8 oracle. The associated documentation clearly defines the scope and boundaries of this implementation.

## Answers to Review Questions

1.  **Does Goal1969 preserve the engine app-agnostic boundary, or does the new `cupy_extent` path smuggle app-specific behavior into the native engine?**
    Goal1969 preserves the engine app-agnostic boundary. The `cupy_extent` path is implemented as a partner-side (Python+CuPy) solution that uses general bounding box intersection logic. The `POLYGON_EXTENT_RAWKERNEL_SOURCE` operates on generic geometric extent properties (min/max coordinates, area) and does not embed app-specific polygon semantics into the native engine. The `docs/reports/goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md` explicitly states: "This does not add app semantics to the native engine. It is a partner-side candidate-table construction path for bounded 2D extents."

2.  **Is the performance interpretation bounded correctly?**
    Yes, the performance interpretation is bounded correctly.
    *   **Comparison baseline**: The `fairness_note` in `examples/rtdl_control_apps_cupy_rawkernel.py` and the reports clearly state that "v2 uses Python+CuPy RawKernel+RTDL under the explicit user decision" and is "Compared against v1.8 Python+RTDL without user C/C++ extension."
    *   **OptiX RT-core result**: The report explicitly mentions: "This is still not an OptiX RT-core result because the pod lacks the OptiX SDK."
    *   **General polygon overlay claim**: The report clarifies: "It does not prove arbitrary polygon overlay acceleration."
    These statements accurately define the scope and limitations of the performance claims.

3.  **Are the tests and report sufficient for this narrow implementation slice?**
    Yes, both the tests and the report are sufficient.
    *   **Tests (`tests/goal1969_cupy_extent_polygon_candidate_backend_test.py`)**: Verifies the existence and functionality of the `cupy_extent` backend, its exposure in the performance script, and the correctness of the `cpu_fallback`. Crucially, it also programmatically validates key assertions made within the `docs/reports/goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md` and checks the recorded performance ratios and correctness flags in the `goal1969_pod_cupy_extent_polygon_control_perf.json` artifact.
    *   **Report (`docs/reports/goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md`)**: Provides a clear and concise explanation of the problem, the implemented solution, its boundaries, and the performance results from the pod test. It also links to the raw JSON artifact.

4.  **Does this support the design lesson that v2 needs compact partner-owned candidate/payload table construction, not dense all-pairs handoff?**
    Yes, the evidence strongly supports this design lesson. The report explicitly states that `cpu_all_pairs` candidate construction was "catastrophic" and that Embree discovery was "still too expensive." The significant performance speedup (up to `0.281x` of v1.8 median time) achieved by the `cupy_extent` backend demonstrates that an efficient, compact partner-owned candidate-table handoff is critical for performance in these scenarios, highlighting its importance over the exact continuation math. The report concludes: "The useful lesson is that a compact partner candidate-table handoff matters more here than the exact CPU/GPU continuation math."

## Conclusion

The Goal1969 implementation effectively resolves the identified bottleneck in candidate construction for the specified polygon control rows. The solution is well-defined, correctly implemented, and thoroughly documented with appropriate performance measurements and boundary statements. The results reinforce the architectural lesson regarding the necessity of compact, partner-owned candidate/payload table construction in v2.
