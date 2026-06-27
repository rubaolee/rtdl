# Goal1007 External Review Request

Please independently review Goal1007, a larger-scale RTX repeat plan for the seven Goal1006 candidates held because their RTX query phases were below the 100 ms public-wording floor.

## Files

- Plan generator: `scripts/goal1007_larger_scale_rtx_repeat_plan.py`
- Pod command script: `scripts/goal1007_larger_scale_rtx_repeat_commands.sh`
- Tests: `tests/goal1007_larger_scale_rtx_repeat_plan_test.py`
- JSON report: `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.json`
- Markdown report: `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.md`
- Source wording gate: `docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.json`

## Review Questions

1. Does the plan cover exactly the seven Goal1006 held candidates?
2. Are the larger-scale commands reasonable as a first cloud repeat batch, especially the high-memory robot run?
3. Is the shell script bounded and safe: it does not create cloud resources, does not authorize claims, and writes explicit output JSON files?
4. Are the risk notes adequate for pod operation and post-run interpretation?

## Expected Output

Write `ACCEPT` or `BLOCK` with concrete findings. If writing to repo is available, save to `docs/reports/goal1007_<reviewer>_external_review_2026-04-26.md`.
