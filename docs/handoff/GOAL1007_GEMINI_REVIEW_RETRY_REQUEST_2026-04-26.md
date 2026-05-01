# Goal1007 Gemini Review Retry Request

Your previous Goal1007 review returned `BLOCK` because it did not inspect the plan files and said risk notes were absent. The risk notes are present in the generated report and source script.

Please perform a bounded re-review by reading these exact files:

- `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.md`
- `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.json`
- `scripts/goal1007_larger_scale_rtx_repeat_commands.sh`
- `scripts/goal1007_larger_scale_rtx_repeat_plan.py`
- `tests/goal1007_larger_scale_rtx_repeat_plan_test.py`

Specific checks:

1. Confirm whether the markdown table contains a `Risk note` column for all seven targets.
2. Confirm whether `build_plan()` compares target app/path pairs against the held Goal1006 candidate set and reports missing/extra targets.
3. Confirm whether the shell script only runs local profiler commands and does not provision cloud resources.
4. Confirm whether the post-review fix prevents `--audit-existing` from rewriting the shell script unless `--output-sh` is explicitly provided.

Write a new verdict to `docs/reports/goal1007_gemini_retry_external_review_2026-04-26.md` with `ACCEPT` or `BLOCK`.
