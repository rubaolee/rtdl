# External Review Request: Goal3052 Partner Choice Pod Refresh

Please independently review Goal3052, the A4000 pod evidence refresh that
followed the Goal3050 partner-choice documentation.

## Files To Inspect

- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02.md`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/raydb_numba_minmax_1m.json`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/triangle_numba_compact_mask_1m.json`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/rayjoin_numba_compact_mask_1m.json`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/grouped_arg_reducer_1m.json`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/hausdorff_active_frontier_small_refresh.json`
- `tests/goal3052_partner_choice_pod_refresh_test.py`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/learn/benchmark_partner_reference_matrix.md`

## Review Questions

1. Does the pod evidence support the Goal3050 guidance that Numba is a real
   selectable custom-kernel partner for selected generic continuations?
2. Does the evidence preserve the boundary that Numba is not automatically
   faster than CuPy, and that CuPy remains the right recommendation for rows
   where it is the measured reference?
3. Does the report correctly disclose the pod environment setup issue
   (`numba` missing initially, installed into the venv, Torch nvjitlink pin
   caveat)?
4. Do the JSON artifacts and test keep all release, broad speedup, RT-core,
   true-zero-copy, and automatic partner-selection claims blocked?
5. Are any numbers or app interpretations misleading?

## Required Output

Write one review file using one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Claude output path:

```text
docs/reviews/goal3053_claude_review_goal3052_partner_choice_pod_refresh_2026-06-02.md
```

Gemini output path:

```text
docs/reviews/goal3053_gemini_review_goal3052_partner_choice_pod_refresh_2026-06-02.md
```

Please state that the review is independent and distinct from Codex authoring.
Do not authorize a v2.6 release, package install wording, broad RT-core speedup
wording, broad CuPy/Numba acceleration wording, true-zero-copy wording, or
hidden partner auto-selection.
