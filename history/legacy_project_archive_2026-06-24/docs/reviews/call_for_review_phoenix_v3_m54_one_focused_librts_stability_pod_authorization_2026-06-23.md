# Call For Review: Phoenix V3 M54 One Focused LibRTS Stability POD Authorization

Date: 2026-06-23

Status: `draft_review_packet_not_authorized`

This packet prepares the next bounded external review recommended by M53. It
does not authorize execution by itself.

## Request

Review whether to authorize exactly one focused LibRTS stability POD run using
the M47/M48/M51 suite.

If authorized, the only allowed token is:

```text
M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED
```

The run scope must be exactly:

- M47/M48 LibRTS stability protocol
- two scenarios
- eight paired samples each
- alternating V2.14/current order
- full preflight capture
- separate current and V2.14 roots
- explicit Linux/POD Python paths
- full copy-back of summary, README, per-command stdout/stderr, and preflight
  artifacts

## Required Review Inputs

- `docs/reviews/claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m51_librts_authorized_runbook_dry_run_20260623/summary.json`

## P1 Items That Must Be Resolved Before Any Run

- A real V2.14 root must be supplied; do not execute dry-run placeholder command
  lines containing `<v2-root-required-on-execute>`.
- Explicit Linux/POD Python paths must be supplied for both current and V2.14;
  do not use the local Windows `C:\Python311\python.exe` dry-run default.

## Requested Verdict Labels

- `authorize_m47_one_focused_librts_stability_pod_run`
- `revise_m54_missing_p1_execution_preconditions`
- `reject_m54_pod_authorization_not_safe`

## Review Questions

1. Is the M47/M48/M51 suite ready for exactly one focused LibRTS stability POD
   run once real roots and Linux/POD Python paths are supplied?
2. Are the two M53 P1 items fully captured as pre-execution requirements?
3. Does the M51 runbook require full evidence copy-back before interpretation?
4. Does the M52 authorization-surface audit confirm that only M47 token-gated
   execution is in scope for this request?
5. If authorization is granted, is it limited to exactly one focused LibRTS
   stability run and no broader spend?

## Non-Authorization Boundaries

Even if the focused run is authorized, this review must not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

If the verdict is not exactly
`authorize_m47_one_focused_librts_stability_pod_run`, the token must remain
blocked.
