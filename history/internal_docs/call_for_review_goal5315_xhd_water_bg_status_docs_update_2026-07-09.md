# Call For Review - Goal5315 X-HD WaterBodies/BG Status Docs Update

Please strictly review Goal5315:

```text
history/internal_docs/goal5315_xhd_water_bg_status_docs_update_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
history/internal_docs/xhd_current_status_after_goal5314_2026-07-09.md
tests/goal5315_xhd_water_bg_status_docs_test.py
```

Evidence dependencies:

```text
history/internal_docs/goal5313_xhd_water_bg_author_config_alignment_result_2026-07-09.md
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
```

## Review Questions

1. Does the results README now expose the corrected WaterBodies/BG comparison
   clearly enough for a user to avoid using Goal5311's `n_points_cell=15` run as
   the paper-log denominator?
2. Does the review register correctly mark Goals5313 and 5314 as
   `implemented_review_pending`, not externally reviewed?
3. Does the current-status document correctly state that the full X-HD objective
   remains incomplete?
4. Does it preserve the corrected WaterBodies/BG scalar result without
   overclaiming exact WKT recovery, Figure 5 completion, performance parity, or
   identical numeric precision?
5. Are the tests sufficient to pin the key status text and prevent regression
   to the old denominator confusion?
6. Is Goal5316, a consolidated Figure-5 / Level-B status matrix, the right next
   step?

## Expected Answer Shape

```text
Verdict: approve_goal5315_xhd_water_bg_status_docs_update
or
Verdict: revise_goal5315_...

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to the 6 questions:
1. ...
...
6. ...
```
