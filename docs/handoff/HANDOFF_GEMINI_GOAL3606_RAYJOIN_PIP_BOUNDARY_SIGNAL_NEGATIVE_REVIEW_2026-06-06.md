# Handoff: Gemini Review Goal3606 RayJoin PIP Boundary Signal Negative Probe

Please perform a read-only independent Gemini review of Goal3606 and write the review to:

`docs/reviews/goal3607_gemini_review_goal3606_rayjoin_pip_boundary_signal_negative_2026-06-06.md`

## Files To Read

- `docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_2026-06-06.md`
- `docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_a5000/summary.json`
- `tests/goal3606_rayjoin_pip_boundary_signal_4096_negative_test.py`
- `docs/reports/goal3604_rayjoin_pip_boundary_event_signal_timing_2026-06-06.md`
- `docs/reviews/goal3605_gemini_review_goal3604_rayjoin_pip_signal_timing_2026-06-06.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal3606 correctly report that the Goal3388 boundary-event selected-point signal fails exactness on the 4096-chain public-CDB county slice under all tested tolerances?
2. Does this evidence correctly block default-route promotion for that signal family?
3. Is the current route guidance still correct: CuPy dense for public-CDB PIP scalar count, prepared OptiX exact for no-partner RTDL-only count, future fused generic closed-shape membership/count primitive for RTDL-side acceleration?
4. Are the claim boundaries strong enough?

## Required Review Shape

- Start with `Verdict: accept`, `Verdict: accept-with-boundary`, `Verdict: needs-more-evidence`, or `Verdict: reject`.
- State that this is an independent Gemini review, distinct from Codex.
- Lead with findings ordered by severity.
- Include file-level references.
- Do not edit source, report, or artifact files except for writing the review file above.
