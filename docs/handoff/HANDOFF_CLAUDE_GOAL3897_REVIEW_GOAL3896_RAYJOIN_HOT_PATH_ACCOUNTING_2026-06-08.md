# Handoff: Claude Review Goal3896 RayJoin Hot-Path Accounting

Please perform a read-only external review of Goal3896.

## Files To Inspect

- `scripts/goal3866_rayjoin_representative_scale_profile.py`
- `tests/goal3896_rayjoin_hot_path_accounting_test.py`
- `tests/goal3896_rayjoin_hot_path_accounting_a5000_test.py`
- `docs/reports/goal3896_rayjoin_hot_path_accounting_2026-06-08.md`
- `docs/reports/goal3896_rayjoin_hot_path_accounting_a5000/summary.json`
- `docs/reports/goal3896_rayjoin_hot_path_accounting_a5000/exit_code`
- `docs/reports/goal3896_rayjoin_hot_path_accounting_a5000/run.stderr`
- Related context:
  - `docs/reports/goal3866_rayjoin_representative_scale_profile_2026-06-08.md`
  - `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000_2026-06-08.md`
  - `docs/reviews/goal3895_claude_review_goal3894_clean_provenance_scale_smoke_2026-06-08.md`

## Review Questions

1. Does Goal3896 correctly separate RayJoin wrapper elapsed time from per-contract hot-path metrics?
2. Are the four route recommendations supported by the artifact: Numba for one-shot PIP, RTDL/OptiX prepared batch executor for repeated PIP, RTDL/OptiX prepared segment-pair count for LSI, and RTDL/OptiX prepared shape-pair active count for overlay?
3. Does the clean A5000 artifact show `exit_code=0`, all counts matching, source commit `23723c6e`, empty `git_status_short`, and real A5000 metadata?
4. Does the new hot-path summary preserve all claim-boundary flags as false and avoid whole-app RayJoin/public speedup/paper reproduction/automatic dispatch overclaims?
5. Is this accounting hardening, not a native-engine app-specific change?

## Expected Output

Write your review to:

`docs/reviews/goal3897_claude_review_goal3896_rayjoin_hot_path_accounting_2026-06-08.md`

Use a verdict of `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source files other than writing the review file. If you cannot run tests, state that limitation and still do a read-only code/artifact review.
