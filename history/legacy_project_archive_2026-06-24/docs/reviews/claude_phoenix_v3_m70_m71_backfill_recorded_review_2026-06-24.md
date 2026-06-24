# Claude Review: Phoenix V3 M70/M71 Backfill Combined Summary

Date: 2026-06-24

Reviewer: Claude (Anthropic claude-sonnet-4-6, external critical review seat)

Call for Review: `docs/reviews/call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md`

M70 Recorded Review: `docs/reviews/claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md`

M71 Recorded Review: `docs/reviews/claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md`

Status: `claude_backfill_m70_m71_complete_pending_final_3ai_consensus_no_execution_no_pod`

---

## Summary of Verdicts

| Milestone | Verdict |
| --- | --- |
| M70 | `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod` |
| M71 | `accept_m71_local_dry_run_gate_continue_no_execution_no_pod` |

Both verdicts are positive accepts. The intake validator may now advance to
status `claude_backfill_intake_accept_no_authorization`. Codex must draft the
final 3AI consensus for M70 and M71 and run the goal completion audit before
either milestone is marked goal-complete.

---

## Basis for Each Verdict

### M70 RTNN Focused Protocol Draft

Accepted because:

1. All 7 frozen RTNN shape groups and all 14 rows are named with exact
   same-contract incumbents for both embree and optix backends.
2. Every M69 carry-forward item is present verbatim: uniform-only repeat50
   phase evidence, per-distribution bounds required for clustered/shell, full-
   batch self-query constraint, exact shapes/incumbents required, 0.988781x
   hot-query boundary visible, aggregate/runner/bridge/diagnostic rows not merged.
3. All 10 phase metrics are named and must remain separate; `must_keep_separate:
   true`.
4. Nine fail-closed stop conditions cover RTNN app tuning, repeat50 overclaiming,
   contract mixing, and any unauthorized scope (public/release/POD/V4/embedding/
   C ABI/true-zero-copy/route-specific tuning/watch-row closure).
5. No commands, no authorization token, no execution path. All authorization
   flags false.

### M71 RTNN Local Harness Dry-Run Gate

Accepted because:

1. The packet is dry-run throughout: `dry_run_gate_only: true`,
   `benchmark_execution_authorized: false`, `commands_generated: false`,
   `authorization_token_present: false`, `command_present: false` for all 7
   shape groups.
2. The RTNN app change exposes correctly separated `input_load`, `input_pack`,
   `input_load_pack`, `runner_after_input_load_pack`, `hot_query_median`, and
   `signature_match_status` fields. Verified in source code at
   `rtnn_prepared_execution_ranked_summary_payload`.
3. The dry-run plan covers all 7 M70 shape groups and all 14 rows exactly.
4. Source-surface checks confirm generic helper call, productized mode, full-
   batch self-query constraint, telemetry split helper, and no route-specific
   tuning (`native_engine_customization: False` throughout).
5. All non-authorization flags false. No unauthorized release label.

---

## Supplemental Findings: Backfill Packet and Intake

### Is the Antigravity M70 review acceptable as a provisional second seat?

Yes. Antigravity issued a properly scoped accept verdict with P0/P1/P2
findings, answered all review questions, and carried the complete non-
authorization block. It correctly named the P1-A app-win gap (13/14 rows below
1.05x) and P1-B hot-query regression (0.988781x) as load-bearing constraints.
It is acceptable as the second AI seat for the provisional 2AI consensus.

### Is the Antigravity M71 review acceptable as a provisional second seat?

Yes. Antigravity issued a properly scoped accept verdict, verified the telemetry
fields in source, confirmed 7 shape groups and 14 rows, verified source-surface
checks, and preserved all non-authorization boundaries. Acceptable as the second
AI seat for the provisional M71 2AI consensus.

### Is the Antigravity packet/intake review acceptable as a non-completion, non-authorizing external check?

Yes. Antigravity's verdict `accept_m70_m71_backfill_packet_intake_continue_wait_for_claude`
is correctly scoped as a structural and process check. It does not declare M70/M71
complete and does not authorize any execution action. The P1-B it raised (lack
of CLI exit-code fail-closed) was addressed before this review: the intake CLI
now exits with code 1 for pending/blocked statuses unless `--allow-non-accepted`
is explicit. This fix is verified in source and in the intake test suite.

### Does the intake validator fail closed after the P1-B fix?

Yes. `v3_phoenix_m70_m71_claude_backfill_intake.py` calls `sys.exit(1)` at line
277 when `payload["status"] != "claude_backfill_intake_accept_no_authorization"`
and `--allow-non-accepted` is not set. The test `test_cli_fails_closed_unless_non_accepted_is_explicitly_allowed`
in `tests/v3_phoenix_m70_m71_claude_backfill_intake_test.py` verifies this
behavior. The fix is correct.

### Does the completion-audit builder avoid self-authorizing M70/M71 completion?

Yes. `v3_phoenix_m70_m71_goal_completion_audit.py` has
`"goal_completion_authorized": False` hardcoded unconditionally. The audit
advances status to `m70_m71_goal_completion_ready_for_final_3ai_consensus_no_authorization`
only when the intake accepts both reviews and all required support files are
present — and even then the status ends with `_no_authorization`. The audit does
not declare completion; it signals readiness for a final 3AI consensus step.

---

## Direct Answers to All Backfill Call-for-Review Questions

1. **Does M70 correctly name all exact frozen RTNN shapes and same-contract
   incumbents?** Yes. See M70 recorded review, Q1.

2. **Does M70 preserve the M69 boundaries?** Yes. All six carry-forward items
   verified. See M70 recorded review, Q2.

3. **Does M70 remain a protocol draft only?** Yes. All authorization flags
   false, no commands, no authorization token. See M70 recorded review, Q3/Q8.

4. **Does M71 remain dry-run only?** Yes. See M71 recorded review, Q1.

5. **Does the M71 telemetry-only app change correctly expose the required
   fields?** Yes. Verified in source. See M71 recorded review, Q2.

6. **Does M71 cover all 7 M70 shape groups and 14 rows?** Yes. See M71
   recorded review, Q3.

7. **Are the Antigravity M70/M71 reviews acceptable as provisional second
   seats?** Yes. See supplemental findings above.

8. **Is the supplemental Antigravity packet/intake review acceptable as a
   non-completion, non-authorizing external check?** Yes. See supplemental
   findings above.

9. **Does the intake validator fail closed after the P1-B fix?** Yes. See
   supplemental findings above.

10. **Does the completion-audit builder avoid self-authorizing M70/M71
    completion?** Yes. See supplemental findings above.

11. **What exact carry-forward requirements remain before any execution
    protocol can be proposed?**

    a. Final 3AI consensus for M70 and M71 must be written by Codex, based
       on this Claude backfill and the existing Antigravity/Codex seats.
    b. Goal completion audit must confirm readiness and be recorded.
    c. A new protocol review, separate from M70/M71, must be proposed and
       accepted by 3AI consensus before any benchmark execution is authorized.
    d. Per-distribution phase bounds for clustered and shell distributions
       must be established in that execution protocol.
    e. The 0.988781x hot-query boundary must remain visible and must not be
       presented as a speedup.
    f. The app-win gap (13/14 rows below 1.05x, overall geomean ~1.003x)
       must be treated as the primary risk in any execution protocol.
    g. No execution protocol may authorize POD, runbook, all-app run, or
       public speedup claim without a separate, explicit 3AI authorization.

---

## Explicit Non-Authorization Block

This review carries an explicit non-authorization block. No matter the verdict:

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
