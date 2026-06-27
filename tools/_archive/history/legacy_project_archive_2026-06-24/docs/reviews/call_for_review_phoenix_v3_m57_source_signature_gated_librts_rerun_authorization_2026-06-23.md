# Call For Review: Phoenix V3 M57 Source-Signature-Gated LibRTS Rerun Authorization

Date: 2026-06-23

Status: `draft_review_packet_not_authorized`

## Request

Review whether Phoenix V3 may run exactly one future focused LibRTS M47 rerun
after the M56 source-signature repair.

This packet requests authorization only for one rerun of:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

The proposed token is:

```text
M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

This packet does not authorize execution by itself. The token remains blocked
unless the final 3-AI consensus verdict explicitly authorizes it.

## Why A Rerun Is Being Requested

M55 consumed the M54 one-run token and produced valid red/open evidence. Both
LibRTS scenarios failed because current metadata lacked:

```text
prepared_execution_session_runner_metadata.set_b_control_candidate=true
```

M56 diagnosed that the productized runner did execute and added required
preflight row:

```text
current_librts_set_b_source_signature
```

A single source-signature-gated rerun is the smallest way to determine whether
the actual POD runtime payload now emits the required Set-B metadata and whether
the two LibRTS watch rows remain red/yellow/green under the unchanged M47
protocol.

## Required Inputs

- `docs/reports/phoenix_v3_m56_librts_set_b_metadata_diagnosis_and_preflight_repair_2026-06-23.md`
- `docs/reports/phoenix_v3_m56_goal_completion_audit_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m56_goal_completion_3ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m55_goal_completion_3ai_consensus_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `tests/v3_phoenix_m56_librts_set_b_metadata_diagnosis_test.py`

## Required Execution Conditions If Authorized

If and only if this packet is authorized by final 3-AI consensus, the executor
must satisfy all conditions below:

1. Use exactly one run of `scripts/v3_phoenix_m47_librts_stability_protocol.py`.
2. Use token `M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`.
3. Use the unchanged M47 scenario set: `optix_cold_single_shot` and
   `embree_32768_stress`.
4. Use exactly 8 paired samples per scenario.
5. Use real current and V2.14 roots, not placeholders.
6. Use explicit Linux/POD Python paths.
7. Run target-machine dry-run first with `--run-preflight`.
8. Do not execute measured samples unless target dry-run reports
   `failed_checks=[]`.
9. Confirm the target dry-run includes required preflight row
   `current_librts_set_b_source_signature`.
10. If `current_librts_set_b_source_signature` fails, stop immediately and copy
    back the failed dry-run evidence; do not run measured samples.
11. Copy back full evidence: `summary.json`, `README.md`, all measured
    stdout/stderr files, preflight files, and driver logs.
12. Interpret copied evidence only through a later review packet. Do not close
    watch rows from raw run output.

Code-level fail-closed hardening:

- `scripts/v3_phoenix_m47_librts_stability_protocol.py` now aborts before
  `execute_schedule()` if `execute_preflight()` returns any preflight error.
- `scripts/v3_phoenix_m47_librts_stability_protocol.py` supports
  `--run-preflight`, which executes preflight rows during dry-run without
  executing measured samples.
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py` includes
  `test_execute_aborts_before_samples_when_preflight_fails`.

## Requested Verdict Labels

Choose exactly one:

- `authorize_m57_one_source_signature_gated_librts_rerun`
- `request_m57_changes_before_authorization`
- `reject_m57_rerun_authorization`

## Review Questions

1. Does M56 provide enough local repair evidence to justify exactly one
   source-signature-gated rerun?
2. Are the M57 execution conditions narrow enough to prevent another broad POD
   campaign?
3. Does the proposed token avoid reusing the consumed M54/M55 token?
4. Does the required `current_librts_set_b_source_signature` dry-run preflight
   adequately address the known M55 metadata failure before measured samples?
5. Are the residual risks from M56 correctly carried forward, especially that a
   metadata-fixed rerun may still be performance-red?
6. If authorized, is the next allowed action only target dry-run, then exactly
   one execution if the dry-run passes?

## Non-Authorization

This review must not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure
- no scenario changes
- no sample-count changes
- no second M57 run

## Goal-Level Decision Audit

Decision: request review for one future source-signature-gated LibRTS rerun,
but do not execute it now.

1. Was I foolish? No, if this remains review-only.
2. If yes, what actions made the decision foolish? It would be foolish to run
   the POD immediately, reuse the consumed M54 token, or treat metadata repair
   as performance success.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Preserve M55 as red/open evidence and request a new bounded
   authorization packet after M56 repair.
4. Can I now try a different path that actually solves the problem? Yes. Ask
   external reviewers whether one source-signature-gated rerun is justified,
   then execute only if final 3-AI consensus authorizes it.
