# Handoff: Goal1954 Gemini Review Of RawKernel Control-App v2 Decision

Please independently review Goal1953.

## Files To Read

- `docs/reports/goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md`
- `examples/rtdl_control_apps_cupy_rawkernel.py`
- `tests/goal1953_control_apps_cupy_rawkernel_v2_test.py`
- `docs/reports/goal1952_partner_rawkernel_and_user_continuation_boundary_2026-05-13.md`
- `docs/partner_acceleration_boundaries.md`

## Context

The user explicitly decided that the four former control apps may use CuPy
`RawKernel` continuations as their v2.0 app versions:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

They may be compared against v1.8 Python+RTDL baselines with no user C/C++
extension, but the report must preserve the fairness note that this comparison
is not absolutely fair.

## Review Questions

1. Does the implementation preserve the user decision accurately?
2. Does the CPU fallback prove local app-result parity without overclaiming
   performance?
3. Are the four app summaries compared to appropriate v1.8 Python+RTDL oracles?
4. Does the report correctly block speedup claims until real CuPy pod timing is
   collected?
5. Are the claim boundaries consistent with Goal1952 and
   `docs/partner_acceleration_boundaries.md`?

## Expected Output

Write:

`docs/reviews/goal1954_gemini_review_goal1953_rawkernel_control_apps_2026-05-13.md`

Use one final verdict from:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is a review only. Do not perform pod timing.
