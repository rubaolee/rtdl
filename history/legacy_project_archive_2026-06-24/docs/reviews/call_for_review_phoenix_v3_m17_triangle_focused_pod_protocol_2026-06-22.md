# Call For Review: Phoenix V3 M17 Triangle Focused POD Protocol

Date: 2026-06-22

Status: `request_m17_protocol_review_not_pod_run`

This asks for strict review of the M17 protocol. It does not authorize release
or POD spend by itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

## Packet

- M17 JSON:
  `docs/rebuild/v3/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.json`
- M17 report:
  `docs/reports/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md`
- M16 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m16_triangle_runner_wiring_2ai_consensus_2026-06-22.md`
- Old Triangle row:
  `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json`

## Review Questions

1. Is the row definition serious enough for the third strict Set-A probe?
2. Are the three variants correct: Embree control, legacy OptiX app-front-door,
   and M16 productized runner?
3. Is it correct that the current app CLI does not by itself satisfy the M16
   productized-runner POD harness requirement?
4. Should the next step be M18 runner harness only, with no POD?
5. Or is one focused POD run authorized after a harness gate passes?
6. Are the success bars correct: oracle match, M16 metadata, runner OptiX over
   Embree >=1.20x, and runner-vs-legacy wall >=0.98x?
7. Is any release, public speedup, broad V3-over-V2, all-app, V4, or zero-copy
   claim authorized? My position: no.

## Requested Verdict Labels

Choose exactly one:

- `accept_m17_authorize_m18_runner_harness_no_pod`: protocol direction is
  correct; next write and locally test the runner harness only.
- `accept_m17_authorize_one_focused_triangle_pod_after_harness_gate`: protocol
  is correct and one focused POD run may start after the runner harness exists,
  passes local tests, and preserves all controls.
- `revise_m17_protocol`: require protocol fixes before M18 or POD decisions.
- `reject_m17_protocol`: this is the wrong Triangle path for the third strict
  Set-A probe.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- focused POD authorization now: yes/no
- all-app POD authorization now: yes/no
- whether M17 protocol is sufficient
- whether a runner harness is a pre-run blocker
- whether Triangle counts as the third strict Set-A material probe now

Please be strict. The goal is to test Phoenix V3 runtime-trunk capability, not
to rerun a strong old Triangle app row and pretend it proves the current runner.

## Goal-Level Decision Audit

Decision: seek 2-AI review for M17 protocol before any runner harness or POD
run.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be spending POD from the old Triangle packet without
   proving the current M16 productized route can be measured.
3. Was there another path?
   Yes: run immediately. That would skip the harness/protocol gate.
4. Can I now try a different path?
   Yes: review this protocol, then build M18 harness or run exactly one focused
   POD only if 2-AI authorizes it.
