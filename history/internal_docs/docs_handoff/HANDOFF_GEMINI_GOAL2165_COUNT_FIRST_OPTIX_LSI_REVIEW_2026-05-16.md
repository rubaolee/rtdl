# Handoff: Gemini Review For Goal2165 Count-First OptiX LSI Output

Please perform an independent read-only review of Goal2165.

## Context

Goal2161 showed that CuPy brute-force beat one-shot OptiX on bounded public CDB RayJoin LSI slices. Goal2163 added a generic prepared OptiX segment-pair-intersection surface and reached parity/small wins. Goal2165 changes the generic OptiX LSI launch to count candidates first, allocate only the actual candidate-count output buffer, then rerun to write candidate records before the existing host exact refinement.

This must remain app-agnostic: the native primitive is generic segment-pair intersection, not a RayJoin-specific engine continuation.

## Files To Review

- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal2165_segment_pair_intersection_count_first_output_test.py`
- `docs/reports/goal2165_count_first_optix_lsi_output_2026-05-16.md`
- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count192_pod_2026-05-16.json`
- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count256_pod_2026-05-16.json`
- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count384_pod_2026-05-16.json`
- `tests/goal2165_count_first_optix_lsi_output_report_test.py`

## Review Questions

1. Does the count-first candidate-output protocol preserve the generic app-agnostic engine boundary?
2. Does the implementation preserve the existing correctness model by keeping host exact refinement?
3. Do the pod artifacts support the report's precise speedup claims over the same-runner CuPy brute-force baseline?
4. Is the report conservative enough about broad RT speedup, full RayJoin reproduction, and v2.0 release readiness?
5. Are there blocking debts that should prevent Goal2165 from being treated as a v2.0 performance-design improvement?

## Required Output

Write your review to:

`docs/reviews/goal2166_gemini_review_goal2165_count_first_optix_lsi_output_2026-05-16.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state explicitly that this is an independent Gemini review distinct from Codex authoring, and that it does not by itself authorize v2.0 release.
