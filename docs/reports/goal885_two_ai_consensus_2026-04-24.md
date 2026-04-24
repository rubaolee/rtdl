# Goal885 Two-AI Consensus

Date: 2026-04-24

## Verdict

Consensus: `ACCEPT`.

Codex refreshed the RTX cloud single-session runbook so it matches the current
active and deferred v0.9.8 RT-core work. Claude independently reviewed the
runbook, tests, and Goal885 report and returned `ACCEPT` in
`docs/reports/goal885_claude_external_review_2026-04-24.md`.

## Agreed Scope

- Run the active one-shot evidence batch first.
- If the pod remains healthy, run the same-pod deferred exploration batch.
- The deferred batch covers all 10 current deferred RTX targets.
- Deferred failures are artifacts for follow-up work, not public RTX claim
  evidence.
- The pod policy remains one session, no per-app restarts.

## Cloud Start State

After this Goal885 package is committed and pushed, local runbook/readiness
work is sufficient to start a pod for the active batch plus the same-pod
deferred exploration batch. If more local code changes are added before cloud,
rerun the pre-cloud readiness gate first.

