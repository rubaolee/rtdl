# Call For Review: Phoenix V3 M20 Scorecard Sync After Triangle M19

Date: 2026-06-22

Status: `request_m20_next_gate_review_no_pod`

This review asks what Phoenix V3 should do next after M19 closed Triangle as
the third strict Set-A material runtime-trunk probe and the Set-A/Set-B
scorecard was synced to `3/2` focused probes.

This packet does not authorize all-app POD, release, public speedup wording, or
broad V3-over-V2 wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Packet

- M20 sync report:
  `docs/reports/phoenix_v3_m20_scorecard_sync_after_triangle_m19_2026-06-22.md`
- Set-A/Set-B classification:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`
- Set-A/Set-B scorecard gate:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- M19 Triangle result report:
  `docs/reports/phoenix_v3_m19_triangle_env_corrected_pod_result_2026-06-22.md`
- M19 Triangle result review:
  `docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_pod_result_review_2026-06-22.md`
- M19 Triangle result consensus:
  `docs/reviews/codex_claude_phoenix_v3_m19_triangle_result_2ai_consensus_2026-06-22.md`
- Current handoff:
  `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`

## Current Facts

Focused productized material probes:

```text
verified: 3
required_before_full_all_app_pod_run: 2
missing: 0
```

Probe ledger:

```text
aabb_runner_m2_1
hausdorff_threshold_runner_m5_after_m6_1
triangle_m19_env_corrected_productized_runner
```

Frozen current all-app scorecard still blocks release/all-app:

```text
Set A geomean: 1.013x
Set A apps over 1.05x: 1 / 5 required
Set A severe regression apps: barnes_hut=0.844x
Set B geomean: 1.007x
Set B rows below 0.95x: librts_spatial_index embree AABB=0.869x
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
```

Local verification after sync:

```text
tests.v3_phoenix_set_ab_scorecard_gate_test
tests.v3_phoenix_m18_triangle_runner_harness_packet_test
tests.v3_phoenix_triangle_runner_m18_pod_ab_test
Ran 16 tests: OK

JSON parse gate: OK
v3_release_wording_gate: pass
```

## Question

Does M20 authorize preparation of an all-app POD protocol now, or should Phoenix
V3 first do more local/focused generic runtime work on the remaining blockers?

The current Codex position:

```text
all_app_pod_run_now: no
all_app_pod_protocol_preparation: maybe, if external review agrees
next likely blockers to inspect locally/focused before all-app:
  - Barnes-Hut Set-A severe regression, even though focused runtime path evidence exists
  - LibRTS Set-B Embree AABB parity row, even though focused Embree count-only regression was previously recovered
```

## Requested Verdict Labels

Choose exactly one:

- `authorize_m20_all_app_protocol_preparation_no_run`: prepare a strict all-app
  POD protocol packet, but do not run all-app until that packet receives a
  separate external authorization.
- `deny_m20_all_app_protocol_prepare_fix_blockers_first`: do not prepare
  all-app yet; first do more local/focused work on named blockers.
- `revise_m20_scorecard_packet`: require specific scorecard/report edits before
  deciding.
- `reject_m20_path`: the scorecard path is wrong; propose a replacement path.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- all-app POD run authorization now: yes/no
- all-app POD protocol preparation authorization now: yes/no
- whether Triangle remains closed as the third strict Set-A probe: yes/no
- next concrete blocker or next concrete packet

## Goal-Level Decision Audit

Decision: ask external review before preparing or spending all-app POD after
M19 pushed focused probes to 3/2.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to treat 3/2 focused probes as automatic all-app run
   authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Run all-app immediately. That would repeat the earlier mistake of
   spending POD before the current blockers and protocol are reviewed.
4. Can I now try a different path that actually solves the problem?
   Yes. Ask for a bounded M20 verdict; then either prepare the all-app protocol
   or fix the named blockers first.
