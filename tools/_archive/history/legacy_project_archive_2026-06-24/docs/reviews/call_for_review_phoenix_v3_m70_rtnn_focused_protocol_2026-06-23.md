# Call For Review: Phoenix V3 M70 RTNN Focused Protocol Draft

Date: 2026-06-23

Status: `request_m70_rtnn_focused_protocol_review_no_execution_no_pod`

Please critically review the M70 protocol draft only. It must not authorize
execution unless a later, separate consensus explicitly does so.

## Files To Review

- `docs\rebuild\v3\phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json`
- `docs\rebuild\v3\phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `docs\reports\phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py`

## Specific Questions

1. Does M70 name all exact frozen RTNN shapes and same-contract incumbents?
2. Does it correctly carry the M69 boundary that repeat50 phase evidence is uniform-distribution only?
3. Does it require per-distribution phase bounds before clustered or shell shapes are used?
4. Does it preserve the full-batch self-query constraint?
5. Are hot-query, runner-wall, prepare, and input-loading/packing metrics separated strongly enough?
6. Are the stop conditions enough to prevent RTNN app tuning, repeat50 overclaiming, and contract mixing?
7. Is M71 local harness design/dry-run gate the right next step, with no POD and no runbook execution?
8. Are any non-authorization boundaries weakened?

## Acceptable Verdict Labels

- `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`
- `accept_m70_protocol_shape_but_revise_before_harness`
- `blocked_m70_missing_same_contract_or_phase_boundaries`
- `reject_m70_protocol_repeats_leaf_first_or_overclaims`

If you choose revision/block/reject, list the exact required changes.

## Explicit Non-Authorization Block

No matter the verdict, this review carries: no V3 release, no all-app
benchmark run, no POD spend, no paid POD spend, no focused POD spend,
no runbook execution, no public speedup wording, no broad V3-over-V2
wording, no whole-app speedup wording, no paper reproduction wording,
no RT-core speedup wording, no V4 work, no embedding, no C ABI, no
true-zero-copy claim, no automatic partner selection, no route-specific
RTNN app tuning, and no watch-row closure.

## Goal-Level Decision Audit

Decision: seek external review for an RTNN focused protocol draft before
any harness execution or POD request.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat M69's repeat50 runner-wall signal as
   permission to execute or claim performance.

3. Was there another path?

   Yes. Run a focused RTNN benchmark immediately. That skips the exact
   shape/incumbent/phase-boundary review M69 required.

4. Can I now try a different path that actually solves the problem?

   Yes. Freeze the protocol, get review, and only then build a local harness
   gate if reviewers accept it.
