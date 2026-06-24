# Call For Review: Phoenix V3 M16 Triangle Runner Wiring

Date: 2026-06-22

Status: `request_m16_local_runner_wiring_review_not_release`

This packet asks for strict review of the M16 local implementation. It does not
authorize release or POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
```

## Packet

- M16 JSON:
  `docs/rebuild/v3/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.json`
- M16 report:
  `docs/reports/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md`
- M15 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m15_third_strict_set_a_probe_2ai_consensus_2026-06-22.md`
- Code:
  `src/rtdsl/prepared_execution.py`
  `src/rtdsl/__init__.py`
- Test:
  `tests/v3_phoenix_prepared_execution_session_runner_test.py`

## Proposed Classification

Proposed verdict:

```text
M16 closes local runner wiring for the Triangle third-probe candidate, but does
not close the third strict Set-A material probe.
```

The helper:

```text
run_ray_triangle_weighted_summary_device_output_stream_prepared_session
```

is generic, exported, tested, and produces current Phoenix runner metadata in
local contract tests.

## Questions

1. Does M16 correctly implement the local productized runner helper required by
   M15?
2. Is it correct that this still does not count as the third strict Set-A
   material probe until focused POD A/B runs and is reviewed?
3. Should M17 be a local focused-POD protocol and review packet?
4. Is any focused POD authorized now? My position: no, not until M17 review.
5. Is any all-app POD authorized now? My position: no.
6. Is any release/public/broad V3-over-V2 wording authorized? My position: no.

## Requested Verdict Labels

Choose exactly one:

- `accept_m16_prepare_m17_focused_pod_protocol_no_run`: M16 is locally valid;
  prepare focused POD protocol/review next, but no run yet.
- `accept_m16_authorize_focused_triangle_pod_after_protocol`: M16 is locally
  valid and the next reviewed protocol may authorize one focused POD run if it
  preserves the stated controls.
- `revise_m16_runner_wiring`: require code, metadata, or test fixes before
  protocol work.
- `reject_m16_runner_wiring`: the helper does not satisfy the M15 requirement.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- focused POD authorization now: yes/no
- all-app POD authorization now: yes/no
- whether M16 closes local runner wiring
- whether Triangle counts as the third strict Set-A material probe now

Please be strict. The goal is to keep M16 as productized runtime work, not an
app-specific Triangle shortcut.

## Goal-Level Decision Audit

Decision: seek 2-AI review after local runner wiring before any POD protocol or
run.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be treating local contract wiring as performance
   evidence.
3. Was there another path?
   Yes: run focused POD immediately. That would skip the review gate.
4. Can I now try a different path?
   Yes: record M16, get review, then decide whether M17 may prepare a focused
   POD protocol.
