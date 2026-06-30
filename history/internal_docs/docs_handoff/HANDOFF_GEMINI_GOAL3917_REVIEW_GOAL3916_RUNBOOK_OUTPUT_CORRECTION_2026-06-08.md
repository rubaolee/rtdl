# Handoff: Gemini Review Goal3916 Runbook Output Correction

Please perform a short independent read-only review of Goal3916.

## Context

After Goal3913, a dry-run smoke found that `scripts/goal3866_rayjoin_representative_scale_profile.py` does not accept `--output`; it writes JSON to stdout. Goal3916 corrected `docs/handoff/GOAL3913_SAFE_NEXT_POD_RAYJOIN_RUNBOOK_2026-06-08.md` to redirect stdout to `summary.json` and stderr/progress to `run.log`.

## Files

- `docs/handoff/GOAL3913_SAFE_NEXT_POD_RAYJOIN_RUNBOOK_2026-06-08.md`
- `tests/goal3913_safe_next_pod_rayjoin_runbook_test.py`
- `docs/reports/goal3916_rayjoin_runbook_stdout_output_correction_2026-06-08.md`
- `scripts/goal3866_rayjoin_representative_scale_profile.py`

## Review Questions

1. Does the corrected runbook match the actual CLI contract of `goal3866_rayjoin_representative_scale_profile.py`?
2. Does it keep the PowerShell/SSH safety guards from Goal3913?
3. Does it preserve the claim boundary and make clear that the next pod packet is diagnostic only?

## Required Output

Write to:

`docs/reviews/goal3917_gemini_review_goal3916_runbook_output_correction_2026-06-08.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. State whether tests were run.
