# Gemini Handoff: Review Goal2831 Primitive Payload Column Descriptors

Please perform an independent read-only review of Goal2831 and write the review to:

`docs/reviews/goal2832_gemini_review_goal2831_primitive_payload_column_descriptors_2026-05-31.md`

## Files To Inspect

- `docs/reports/goal2831_primitive_payload_column_descriptors_2026-05-31.md`
- `tests/goal2831_primitive_payload_column_descriptor_test.py`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md`
- `docs/reports/goal2830_goal2829_same_stream_partials_consensus_2026-05-31.md`

## Review Questions

1. Does Goal2831 provide a genuinely generic primitive-payload column descriptor rather than an app-shaped RTNN/RayJoin/DBSCAN API?
2. Does it correctly compose with the neutral-buffer seam, including transfer status, lifetime state, native producer, and fallback reason?
3. Does the Goal2829 same-stream partial path now publish a descriptor for the graph-owned partial buffer without exposing unsafe ownership or claiming broad zero-copy?
4. Are invalid roles and invalid native lifetimes fail-closed in tests?
5. Are claim boundaries strict: no arbitrary partner execution, public speedup, broad true-zero-copy, paper reproduction, whole-app speedup, or v2.5 release claim?
6. Is the proposed next step reasonable: use descriptors to drive a partner-neutral continuation planner for CuPy/Triton/Numba selection with explicit fallback reasons?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict is `accept-with-boundary` unless you find a real correctness, contract, or claim-boundary problem.

Do not modify source files. Only write the review document above.
