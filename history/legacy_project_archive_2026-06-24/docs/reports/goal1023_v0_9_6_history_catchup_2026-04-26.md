# Goal1023 v0.9.6 History Catch-Up

Date: 2026-04-26

Status: accepted by Claude, Gemini, and Codex.

## Problem

Goal1022 proved a release-history drift:

- public docs and release reports identify `v0.9.6` as the current released
  version;
- `docs/release_reports/v0_9_6/audit_report.md` says the release included
  history records through Goal684;
- `history/COMPLETE_HISTORY.md` and `history/revision_dashboard.md` still did
  not mention `v0.9.6` or Goal684.

## Fix

Added an appended, non-rewriting history catch-up round:

- `history/revisions/2026-04-26-goal1023-v0_9_6-history-catchup/metadata.txt`
- `history/revisions/2026-04-26-goal1023-v0_9_6-history-catchup/project_snapshot/goal1023_v0_9_6_history_catchup.md`

Updated public history indexes:

- `history/COMPLETE_HISTORY.md`
- `history/revision_dashboard.md`
- `history/revision_dashboard.html`
- `history/README.md`
- `history/revisions/README.md`
- `history/history.db`

## Verification

Added:

- `tests/goal1023_v0_9_6_history_catchup_test.py`

Expected focused check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1023_v0_9_6_history_catchup_test -v
```

The test asserts that the public history indexes now mention `v0.9.6`,
Goal684, and the Goal1023 catch-up round, and that `history/history.db`
registers the round as accepted.

## Review

- Claude: ACCEPT in `docs/reports/goal1023_claude_review_2026-04-26.md`
- Gemini: ACCEPT in `docs/reports/goal1023_gemini_review_2026-04-26.md`
- Consensus: `docs/reports/goal1023_two_ai_consensus_2026-04-26.md`

## Boundary

This is a history-index repair. It does not rewrite old reports, does not
change the released version, does not tag, and does not authorize public RTX
speedup wording.
