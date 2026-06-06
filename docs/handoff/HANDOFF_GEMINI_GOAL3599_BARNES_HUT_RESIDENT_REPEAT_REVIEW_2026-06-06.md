# Handoff: Gemini Review For Goal3599 Barnes-Hut Resident Repeat Evidence

Please perform a read-only independent review of Goal3599 and write the review to:

`docs/reviews/goal3600_gemini_review_goal3599_barnes_hut_resident_repeat_2026-06-06.md`

## Context

Goal3599 addresses one v2.9 P0 issue from Goal3538: the Barnes-Hut node-coverage row was previously a silent partial row because Goal3536 repeated whole subprocesses and accumulated only about 0.31s of v2.8 hot-query time.

Goal3599 uses the current app-level repeat surface on an RTX A5000:

- mode: `optix_node_coverage_prepared`
- body count: `8192`
- repeat: `1300`
- warmup: `20`
- total measured hot query time: `11.63792886864394s`
- median hot query time: `0.008080567233264446s`
- oracle decision and identity parity: true
- git status: clean

It explicitly does not publish a v2.9-vs-v2.3 speedup ratio because the v2.3 root does not expose the same resident repeat API.

## Files To Read

- `docs/reports/goal3599_barnes_hut_node_coverage_resident_repeat_2026-06-06.md`
- `docs/reports/goal3599_barnes_hut_node_coverage_resident_repeat_a5000/summary.json`
- `tests/goal3599_barnes_hut_node_coverage_resident_repeat_test.py`
- `docs/reports/goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md`
- `docs/reports/goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md`

## Review Questions

1. Does Goal3599 genuinely close the current-main Barnes-Hut silent-partial-row issue for node coverage?
2. Are the artifact fields and report numbers consistent?
3. Is the decision not to publish a v2.9-vs-v2.3 ratio correct given that v2.3 lacks the same repeat API?
4. Are the claim boundaries strong enough: no release, speedup, whole-app Barnes-Hut, RT-BarnesHut reproduction, broad RT-core, zero-copy, or automatic-dispatch claim?
5. What should be the next Barnes-Hut engineering step for v2.9?

## Required Review Shape

- Start with `Verdict: accept`, `Verdict: accept-with-boundary`, `Verdict: needs-more-evidence`, or `Verdict: reject`.
- Lead with findings ordered by severity.
- Include file-level references.
- State that this is an independent Gemini review, distinct from Codex.
- Do not edit source or report files except for writing the review file above.
