# Handoff: External Review For Goal3971 Current-Head Scale Profile

Date: 2026-06-08

Please perform an independent read-only review of Goal3971.

## Commit

- `ad53ff7f` Goal3971 refresh current scale after loader closeout
- `847866a5` Goal3971 add pod setup logs

## Files To Inspect

- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08.md`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/summary.json`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/outputs/`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/final_partner_complete_rerun.log`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/numba_cuda124_fix_rerun.log`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/numba_missing_then_ptx87_mismatch.log`
- `tests/goal3971_current_head_scale_profile_after_loader_closeout_test.py`
- context: `docs/reports/goal3967_direct_cuda_loader_hardening_lane_closeout_2026-06-08.md`
- context: `docs/reports/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_2026-06-08.md`

## Questions To Answer

1. Is the Goal3971 RTX 4000 Ada current-head scale-profile packet valid
   evidence that all 10 benchmark rows pass under the documented partner setup?
2. Does the report correctly explain the partner-toolchain issue:
   missing Numba, then Numba PTX 8.7 versus driver PTX 8.4, then the working
   CUDA 12.4 compiler-package pin plus CuPy?
3. Does the evidence avoid overclaiming release, public speedup, broad RT-core,
   whole-app acceleration, true-zero-copy, AMD performance, package install,
   paper reproduction, automatic partner selection, or app-specific native
   engine logic?
4. Are the Goal3971 tests sufficient to guard the artifact and setup lesson?
5. What should be required before treating this setup as a reusable pod runbook
   rather than a one-off evidence packet?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

- Claude should write:
  `docs/reviews/goal3972_claude_review_goal3971_current_head_scale_profile_2026-06-08.md`
- Gemini should write:
  `docs/reviews/goal3973_gemini_review_goal3971_current_head_scale_profile_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
