# Call For Review: Phoenix V3 M15 Third Strict Set-A Probe Audit

Date: 2026-06-22

Status: `request_candidate_selection_review_not_release`

This packet asks for strict review of the M15 local decision. It does not
authorize release or POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
```

## Packet

- M15 JSON:
  `docs/rebuild/v3/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.json`
- M15 report:
  `docs/reports/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md`
- M14 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m14_runtime_trunk_retarget_2ai_consensus_2026-06-22.md`
- Triangle final row packet:
  `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md`
- Triangle final row consensus:
  `docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md`
- Device-output stream evidence:
  `docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md`
- Non-graph stream closure:
  `docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md`
- Triangle clean target audit:
  `docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.md`

## Proposed Classification

Proposed verdict:

```text
Triangle is the best third strict Set-A candidate, but it is not yet the third
strict Set-A material probe.
```

Reason:

- It has strong row-scoped same-RT-hardware evidence:
  `347.232x` hot OptiX/Embree and `6.342x` wall OptiX/Embree on the exact
  80,000-clique synthetic row.
- It has a real V3-legal physical source: generic prepared ray-batch weighted
  summary, device-output stream continuation, prepared segment replay, and
  explicit partner construction.
- It does not yet have current Phoenix productized-runner evidence with
  `runtime_executed: true`, so it cannot be counted as the third strict probe
  today.

## Questions

1. Is Triangle the correct M16 target for the third strict Set-A candidate?
2. Is it correct to refuse counting the old Triangle row as the third material
   probe until the productized runner path executes it?
3. Should M16 be local-only runner wiring plus protocol, with no POD yet?
4. Is any focused POD authorized now? My position: no.
5. Is any all-app POD authorized now? My position: no.
6. Is any release/public/broad V3-over-V2 wording authorized? My position: no.

## Requested Verdict Labels

Choose exactly one:

- `accept_m15_triangle_m16_local_runner_wiring_no_pod`: accept Triangle as the
  best candidate, require local productized runner wiring/protocol next, no POD.
- `accept_m15_triangle_focused_pod_protocol_now_no_run`: accept Triangle and
  allow preparing a focused POD protocol locally, but still no run.
- `revise_m15_candidate_assessment`: require candidate-analysis fixes before
  deciding.
- `reject_m15_triangle`: Triangle is the wrong candidate; name the better
  candidate and why.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- focused POD authorization now: yes/no
- all-app POD authorization now: yes/no
- whether Triangle counts as the third strict Set-A material probe now
- whether Triangle should be the next local implementation target

Please be strict. The goal is to prevent another premature V3 success claim.

## Goal-Level Decision Audit

Decision: seek 2-AI review before implementing or spending POD on the Triangle
third-probe candidate.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be treating old strong Triangle numbers as a new
   runtime-trunk result without review.
3. Was there another path?
   Yes: implement or run POD immediately. That would skip the measurement
   control M14 required.
4. Can I now try a different path?
   Yes: freeze the candidate selection, get review, and only then do local
   runner wiring or a focused POD protocol.
