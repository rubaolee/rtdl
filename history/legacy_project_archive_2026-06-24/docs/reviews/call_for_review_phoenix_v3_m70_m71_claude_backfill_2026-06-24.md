# Call For Review: Phoenix V3 M70/M71 Claude Backfill

Date: 2026-06-24

Status: `request_claude_backfill_m70_m71_no_execution_no_pod`

This packet exists because Claude was session-limited during M70/M71. Codex and
Antigravity produced provisional 2AI decisions, but M70/M71 cannot be treated as
3AI-complete until Claude backfills the recorded reviews.

## Required Claude Outputs

Claude must write both files:

- `docs/reviews/claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md`

Optionally, Claude may also write a combined summary:

- `docs/reviews/claude_phoenix_v3_m70_m71_backfill_recorded_review_2026-06-24.md`

## M70 Files To Review

- `docs/reviews/call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json`
- `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py`
- `docs/reviews/antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md`
- `docs/reviews/codex_antigravity_phoenix_v3_m70_provisional_2ai_consensus_pending_claude_2026-06-23.md`
- `docs/reports/phoenix_v3_m70_status_pending_claude_backfill_2026-06-23.md`

M70 acceptable verdict labels:

- `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`
- `accept_m70_protocol_shape_but_revise_before_harness`
- `blocked_m70_missing_same_contract_or_phase_boundaries`
- `reject_m70_protocol_repeats_leaf_first_or_overclaims`

## M71 Files To Review

- `docs/reviews/call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json`
- `docs/reports/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- `tests/v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test.py`
- `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `docs/reviews/antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md`
- `docs/reviews/codex_antigravity_phoenix_v3_m71_local_dry_run_gate_provisional_2ai_consensus_pending_claude_2026-06-23.md`
- `docs/reports/phoenix_v3_m71_status_provisional_2ai_pending_claude_2026-06-23.md`

M71 acceptable verdict labels:

- `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`
- `revise_m71_dry_run_gate_before_any_harness_work`
- `reject_m71_dry_run_gate_oversteps_no_execution_boundary`

## Backfill Support Files To Review

- `docs/reports/phoenix_v3_m70_m71_backfill_packet_and_register_status_2026-06-24.md`
- `docs/reviews/external_review_blocked_phoenix_v3_m70_m71_claude_session_limit_2026-06-24.md`
- `docs/reviews/antigravity_phoenix_v3_m70_m71_backfill_packet_intake_review_2026-06-24.md`
- `scripts/v3_phoenix_m70_m71_claude_backfill_intake.py`
- `tests/v3_phoenix_m70_m71_claude_backfill_intake_test.py`
- `scripts/v3_phoenix_m70_m71_goal_completion_audit.py`
- `tests/v3_phoenix_m70_m71_goal_completion_audit_test.py`
- `docs/rebuild/v3/phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.json`
- `docs/reports/phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.md`
- `docs/rebuild/v3/phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.json`
- `docs/reports/phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.md`
- `docs/reports/phoenix_v3_m70_m71_goal_completion_audit_v3_rebuild_2026-06-24.json`

Supplemental review note:

- Antigravity accepted the backfill packet/intake with verdict
  `accept_m70_m71_backfill_packet_intake_continue_wait_for_claude`.
- Antigravity P1-B was addressed: the intake CLI now fails closed by default
  for pending/blocked statuses; pending snapshot generation requires explicit
  `--allow-non-accepted`.

## Questions For Claude

1. Does M70 correctly name all exact frozen RTNN shapes and same-contract
   incumbents?
2. Does M70 preserve the M69 boundaries: uniform-only repeat50 phase evidence,
   per-distribution phase bounds before clustered/shell use, full-batch
   self-query constraint, separated phase metrics, and the `0.988781x`
   hot-query boundary?
3. Does M70 remain a protocol draft only with no execution/POD/runbook/release
   authorization?
4. Does M71 remain dry-run only with no execution path?
5. Does the M71 telemetry-only app change correctly expose separated
   `input_load`, `input_pack`, `input_load_pack`,
   `runner_after_input_load_pack`, `hot_query_median`, and
   `signature_match_status` fields?
6. Does M71 cover all 7 M70 shape groups and 14 rows?
7. Are the Antigravity M70/M71 reviews acceptable as provisional second seats?
8. Is the supplemental Antigravity packet/intake review acceptable as a
   non-completion, non-authorizing external check?
9. Does the intake validator fail closed after the Antigravity P1-B fix?
10. Does the completion-audit builder avoid self-authorizing M70/M71 completion?
11. What exact carry-forward requirements remain before any execution protocol
   can be proposed?

## Explicit Non-Authorization Block

No matter the verdict, this backfill must preserve:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no runbook execution
- no benchmark execution
- no public speedup wording
- no broad V3-over-V2 wording
- no whole-app speedup wording
- no paper reproduction wording
- no RT-core speedup wording
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure
