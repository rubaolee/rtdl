# Codex + Bernoulli 2-AI Consensus: Phoenix V3 M15 Third Strict Set-A Probe Audit

Date: 2026-06-22

Status: `accept_m15_triangle_m16_local_runner_wiring_no_pod`

This consensus records the M15 local candidate-selection review. It is not a
release authorization and authorizes no POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
triangle_counts_as_third_strict_set_a_material_probe_now: false
triangle_next_local_implementation_target: true
```

## Inputs

- M15 JSON:
  `docs/rebuild/v3/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.json`
- M15 report:
  `docs/reports/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md`
- M15 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md`
- M14 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m14_runtime_trunk_retarget_2ai_consensus_2026-06-22.md`
- Triangle row packet:
  `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md`
- Triangle row consensus:
  `docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md`

Local gates before review:

```text
M15 focused tests: 12 tests OK
release wording gate: pass
M15 over-authorization scan: no matches
```

## Bernoulli Verdict

Bernoulli returned:

```text
accept_m15_triangle_m16_local_runner_wiring_no_pod
```

Explicit answers:

- release authorization: no
- public speedup authorization: no
- broad V3-over-V2 authorization: no
- focused POD authorization now: no
- all-app POD authorization now: no
- Triangle counts as the third strict Set-A material probe now: no
- Triangle should be the next local implementation target: yes

Bernoulli found no blockers or P1 fixes for recording M15. The key rationale:
the old Triangle row is strong row-scoped OptiX/Embree evidence, but it is not
current Phoenix `prepared_execution_session_runner` evidence with
`runtime_executed=true`, so it cannot close the third-probe requirement yet.

## Codex Position

Codex accepts the verdict.

Triangle is the correct next local target because it has a real V3-legal
physical source:

- generic prepared ray-batch weighted any-hit summary;
- device-output stream continuation;
- prepared segment replay;
- explicit CuPy/Numba partner construction.

But that source must be routed through the current productized Phoenix runner
before it can count as strict third Set-A material evidence.

## Consensus

Decision: `accept_m15_triangle_m16_local_runner_wiring_no_pod`

- Do not count Triangle as the third strict material probe yet.
- Do not run focused POD now.
- Do not run all-app POD now.
- Do not prepare release or public speedup wording.
- Proceed to M16 local runner wiring/protocol for Triangle.

## M16 Boundary

M16 should be local only. Required metadata:

```text
runtime_executed: true
productized_execution_path: prepared_execution_session_runner
explicit_backend: optix
explicit_partner: cupy_or_numba_as_user_chosen
hot_path_host_materialization: false where supported
m113_graph_capture_claim_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
```

Focused POD remains blocked until M16 is implemented, locally tested, and
reviewed.

## Goal-Level Decision Audit

Decision: accept M15 and proceed only to local Triangle runner wiring.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to convert the old Triangle row into current Phoenix
   runtime-trunk credit before the productized runner executes it.
3. Was there another path?
   Yes: spend POD immediately or count Triangle now. Both would violate the M14
   review boundary.
4. Can I now try a different path?
   Yes. Implement local runner wiring first, then seek review before any
   focused POD.
