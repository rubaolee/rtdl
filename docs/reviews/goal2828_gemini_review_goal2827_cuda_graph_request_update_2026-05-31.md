# Gemini Review for Goal2827: CUDA Graph Request Update

**Date:** 2026-05-31
**Reviewer:** Gemini CLI

## Files Inspected:
- `docs/reports/goal2827_rtnn_cuda_graph_request_update_2026-05-31.md`
- `docs/reports/goal2827_rtnn_cuda_graph_request_update_pod/goal2827_summary.json`
- `tests/goal2827_rtnn_cuda_graph_request_update_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`

## Review Questions and Answers:

### 1. Does Goal2827 preserve the app-agnostic native boundary, with no RTNN-specific ABI or app-shaped native continuation?
**Answer:** Yes. The report explicitly states, "No RTNN-specific native ABI or app-shaped native continuation is introduced." It further clarifies that the contract remains generic, supporting "prepared fixed-radius 3-D search handle," "prepared query-points handle," "unchanged request count," and "updated device arrays for radius and k_max." The test file `tests/goal2827_rtnn_cuda_graph_request_update_test.py` verifies this by asserting that the string "rtnn" is not present in the native workloads.

### 2. Is the request-buffer update correctly constrained to same-shape graph handles with unchanged request count?
**Answer:** Yes. The report's "Purpose" section highlights the intent to "keep the graph topology static, but update the device-resident request buffers for a new same-shape `(radius, k_max)` sweep before replay," explicitly mentioning "unchanged request count." The "Implementation" section reiterates that the update path "requires the same request count as the original graph" and "revalidates radius and `k_max` against the prepared handle." This constraint is also verified by the native code in `rtdl_optix_workloads.cpp` and corresponding tests.

### 3. Does the Python API expose the behavior explicitly through `update_requests(...)`, without making graph replay or graph update the default path?
**Answer:** Yes. The report's "Implementation" section demonstrates the explicit `graph.update_requests(requests_b)` call. The `src/rtdsl/optix_runtime.py` file contains the `update_requests` method within `PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D`. Crucially, the "Claim Boundary" section of the report states that this goal "does not authorize: making graph replay the default path," confirming that the behavior remains opt-in and explicit.

### 4. Does the pod evidence support the narrow claim: exact parity for request set A and updated request set B, with a modest 1.062x update+replay advantage over rebuild+replay in the recorded 32K probe?
**Answer:** Yes. The "Pod Evidence" section of the report, corroborated by `docs/reports/goal2827_rtnn_cuda_graph_request_update_pod/goal2827_summary.json` and `tests/goal2827_rtnn_cuda_graph_request_update_test.py`, confirms exact parity for both direct fused-batch runs and graph replays for request sets A and B. The pod evidence explicitly shows an "update+replay advantage over rebuild+replay" of 1.062x (calculated as 0.000396671 / 0.000373542 from the JSON data, which rounds to 1.062x).

### 5. Does the report keep claim boundaries strict: no public RTDL-beats-CuPy, RTDL-beats-RTNN-paper, broad RT-core, whole-app speedup, or v2.5 release claim?
**Answer:** Yes. The "Claim Boundary" section of the report explicitly lists and disallows all the mentioned claims: "making graph replay the default path; public RTDL-beats-CuPy wording; public RTDL-beats-RTNN-paper wording; paper reproduction wording; whole-app speedup wording; broad RT-core speedup wording; v2.5 release wording." This is reinforced by tests in `goal2827_rtnn_cuda_graph_request_update_test.py` that verify these claim boundaries are set to `false` in the pod summary.

### 6. Is the proposed next step reasonable: return to event-ordered partner chaining rather than continuing micro-optimizing CUDA graph replay?
**Answer:** Yes. The "Next Step" section clearly states: "This completes the obvious graph-reuse slice. The next larger v2.5 step should return to the partner-composition target: event-ordered chaining from device-resident RT/aggregate outputs into partner consumers without a host scalar synchronization boundary." This indicates a strategic shift away from further micro-optimizations of CUDA graph replay, which is a reasonable progression for the project.

## Verdict:
`accept-with-boundary`

**Boundaries:**
*   No public speedup claims beyond the 1.062x measured advantage for the specific 32K probe described.
*   No claims related to RTDL-beats-CuPy, RTDL-beats-RTNN-paper, paper reproduction, whole-app speedup, broad RT-core speedup, or v2.5 release.
*   Graph replay and graph updates are explicitly opt-in via `update_requests(...)` and are not the default path.
*   The `update_requests` functionality is strictly limited to same-shape graph handles with unchanged request counts.
*   Any performance wording must be scoped exclusively to Goal2827.
