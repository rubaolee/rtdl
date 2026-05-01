# Goal1098 Two-AI Consensus

Date: 2026-04-29

## Scope

Goal1098 covers the RTX A5000 pod execution and local intake for the current Goal1084/Goal1093 evidence path:

- Goal1084 facility recentered same-scale validation/timing;
- Goal1093 Barnes-Hut depth-8 4,096-body validation;
- Goal1093 Barnes-Hut depth-8 20M timing-only repeat;
- Goal1096 local copied-artifact intake;
- a local fix so future Goal887 profiler artifacts embed `source_commit` directly.

## AI Reviews

| Reviewer | Verdict | Evidence |
| --- | --- | --- |
| Claude | ACCEPT / evidence supported | `docs/reports/goal1098_claude_review_2026-04-29.md` |
| Codex | ACCEPT | `docs/reports/goal1098_rtx_a5000_goal1084_goal1093_execution_report_2026-04-29.md`, copied artifacts, Goal1096 intake, Goal887 source-commit patch |

## Evidence Summary

| Row | Result |
| --- | --- |
| Facility recentered 2.5M copies / 10M queries | `matches_oracle: true`, `threshold_reached_count: 10000000`, median OptiX query `0.13505441695451736` sec |
| Barnes-Hut depth-8 4,096-body validation | `matches_oracle: true`, `node_count: 65536`, median OptiX query `0.007581695914268494` sec |
| Barnes-Hut depth-8 20M timing | timing-only with `--skip-validation`, `threshold_reached_count: 20000000`, median OptiX query `0.23063642531633377` sec |
| Goal1096 intake | `overall_status: ready_for_2ai_review_not_public_claim`, `blocked_count: 0`, `public_speedup_claim_authorized_count: 0` |

## Source-Commit Handling

The Goal887 profiler did not embed `source_commit` during this pod run. The runner logs recorded `source_commit=58ca06f2573d53754663a2dd10a76207113ab044` before execution, and Codex stamped the same value into the three copied artifacts with a `source_commit_note` that discloses the post-run metadata addition. Timing and result fields were not changed. Claude reviewed this and found the disclosure adequate.

Codex also patched `scripts/goal887_prepared_decision_phase_profiler.py` so future artifacts embed `source_commit` from `RTDL_SOURCE_COMMIT`, `.rtdl_source_commit`, or `git rev-parse HEAD`, and updated `tests/goal887_prepared_decision_phase_profiler_test.py` to verify the field.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 scripts/goal1096_current_rtx_pod_artifact_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal1096_current_rtx_pod_artifact_intake_test tests.goal1097_runbook_goal1096_sync_audit_test
PYTHONPATH=src:. python3 -m unittest tests.goal887_prepared_decision_phase_profiler_test tests.goal1096_current_rtx_pod_artifact_intake_test tests.goal1097_runbook_goal1096_sync_audit_test
git diff --check -- scripts/goal887_prepared_decision_phase_profiler.py tests/goal887_prepared_decision_phase_profiler_test.py docs/reports/goal1098_rtx_a5000_goal1084_goal1093_execution_report_2026-04-29.md docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.md
```

Results:

- Goal1096 intake: `ready_for_2ai_review_not_public_claim`
- Goal1096 + Goal1097 tests: 11 tests, OK
- Goal887 + Goal1096 + Goal1097 tests: 18 tests, OK
- Diff check: OK

## Boundary

Goal1098 does not authorize public README/front-page wording, release, or public RTX speedup claims. The artifacts are RTX evidence that passed local intake and two-AI evidence review. Speedup claims still require same-semantics baselines and a separate public wording review gate.
