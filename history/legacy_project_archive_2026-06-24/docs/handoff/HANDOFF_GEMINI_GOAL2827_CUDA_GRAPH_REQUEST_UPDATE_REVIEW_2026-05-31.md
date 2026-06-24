# Handoff: Gemini Review for Goal2827 CUDA Graph Request Update

Please perform an independent read-only review of Goal2827 and write your
review to:

`docs/reviews/goal2828_gemini_review_goal2827_cuda_graph_request_update_2026-05-31.md`

## Files To Inspect

- `docs/reports/goal2827_rtnn_cuda_graph_request_update_2026-05-31.md`
- `docs/reports/goal2827_rtnn_cuda_graph_request_update_pod/goal2827_summary.json`
- `tests/goal2827_rtnn_cuda_graph_request_update_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`

## Review Questions

1. Does Goal2827 preserve the app-agnostic native boundary, with no RTNN-specific
   ABI or app-shaped native continuation?
2. Is the request-buffer update correctly constrained to same-shape graph
   handles with unchanged request count?
3. Does the Python API expose the behavior explicitly through
   `update_requests(...)`, without making graph replay or graph update the
   default path?
4. Does the pod evidence support the narrow claim: exact parity for request set
   A and updated request set B, with a modest 1.062x update+replay advantage
   over rebuild+replay in the recorded 32K probe?
5. Does the report keep claim boundaries strict: no public RTDL-beats-CuPy,
   RTDL-beats-RTNN-paper, broad RT-core, whole-app speedup, or v2.5 release
   claim?
6. Is the proposed next step reasonable: return to event-ordered partner
   chaining rather than continuing micro-optimizing CUDA graph replay?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please keep any performance wording scoped to Goal2827 only.

