# Claude External Review: Phoenix V3 M68 Next Set-A Family Selection

Date: 2026-06-23

Status: `claude_m68_external_review_accept_no_pod_no_release`

Verdict:
`accept_m68_select_rtnn_ranked_summary_for_m69_local_audit_no_pod_no_release`

## Inputs Read

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md`
- Report:
  `docs/reports/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.json`
- Current handoff:
  `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`
- Frozen scorecard:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- M67 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_3ai_consensus_2026-06-23.md`
- M66 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md`
- RTNN repeat50 evidence report:
  `docs/rebuild/v3/phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md`
- RTNN evidence summary JSON:
  `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json`
- M35 gap ledger:
  `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- M40 component-union intake:
  `docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`
- M43 grouped-reduction report:
  `docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`

## Review Question Responses

### Q1: Is RTNN fixed-radius ranked-summary the right next generic Set-A family?

Yes. The candidate table and exclusion rationale are consistent with the full prior consensus chain:

- **Barnes-Hut excluded**: M67 3-AI consensus correctly accepts it as an existing Step-1
  material family and blocks further Barnes-Hut-specific work. The runner parity is
  `0.999328x` vs the current fused-control — a V3 capability addition, not a
  same-contract V3-over-V2 speedup. No basis to reopen.

- **Spatial/RayJoin excluded**: M66 3-AI consensus confirms non-go for the current
  topology-stream route (`0.973465x` hot query, `0.794180x` process wall against the
  correct incumbent). The current route removes no new physical work. The exclusion is
  correct and properly cited.

- **LibRTS excluded (Set-B)**: LibRTS is a ceiling control, not a generic runtime
  optimization target. M59 confirmed LibRTS as Set-B yellow/open. The packet correctly
  does not treat Set-B control work as a candidate for the next generic Set-A family
  selection.

- **Hausdorff deferred**: Scorecard geomean `1.1485x` — the only Set-A app already
  above the `1.05x` app-win threshold. No near-term urgency. Deferral is warranted.

- **RTNN selected**: Frozen all-app Set-A geomean `1.0033x` — well below the `1.05x`
  threshold. An existing productized `fixed_radius_ranked_summary_3d_prepared_session`
  runner surface is in place and confirmed executing end-to-end. There is a material
  repeat50 runner-wall signal (`1.370176x`) with an explicitly recorded hot-query
  boundary (`0.988781x`). A local bridge audit can test scope before any POD
  commitment. The selection unit is correctly described as a generic runtime family,
  not RTNN app ownership.

The selection logic is sound. RTNN presents the clearest path from an existing runner
signal to a reviewable all-app shape bridge without any of the disqualifying conditions
that apply to the other candidates.

### Q2: Does M68 correctly preserve the repeat50 focused-evidence boundary?

Yes, with one P2 note below.

The packet correctly records both the runner-wall speedup and the hot-query boundary:

- `runner_vs_legacy_runner_wall_speedup: 1.370176x` — repeat50 focused evidence
- `runner_vs_legacy_hot_speedup: 0.988781x` — the runner is slightly slower on the
  hot query than the legacy front door at repeat50; this is the single-shot ceiling

The status label `rtnn_prepared_execution_runner_repeat50_collected_not_release` is
applied consistently across the report, JSON packet, and evidence summary. M69 stop
condition 1 ("If the only positive signal is repeat50 amortization with no all-app
shape bridge, stop") directly addresses the overclaiming risk.

**P2 note — input-packing phase attribution**: The evidence summary shows that runner
`input_load_pack_sec = 1.716s` versus legacy `input_load_sec + input_pack_sec = 1.501s
+ 0.495s = 1.996s` (a difference of ~0.280s). Some of the runner-wall improvement
(`1.370176x`) is attributable to input-packing consolidation rather than execution of
the ranked-summary phase itself. M69 must attribute phase-level wins correctly.
Specifically, the must-answer question "Which phase is actually compressible: prepare,
input packing, ranked-summary aggregate, or runner process wall?" partially covers this,
but an explicit carry-forward instruction to distinguish runtime-trunk phase compression
from packing/loading time consolidation would strengthen M69. This is a note for M69
scope framing, not a blocker for M68 acceptance.

### Q3: Is the proposed M69 scope correct?

Yes. The M69 scope is a local, no-POD phase/shape bridge audit. The must-answer
questions are well-targeted:

1. Which all-app RTNN rows remain below the `1.05x` threshold?
2. Do those rows share the `fixed_radius_ranked_summary_3d` prepared-session surface?
3. Is the repeat50 signal broad enough to justify a focused runbook?
4. Which phase is actually compressible?
5. Does the next change belong in the generic runner/phase bridge?

This sequencing is correct. A bridge audit answering these five questions before any
runbook, POD request, all-app run, or release wording is the appropriate next step.
It mirrors the M67 pattern (local pre-audit before any POD authorization) applied now
to RTNN.

The `pod_authorized: false` and `all_app_authorized: false` constraints in the JSON
`next_work` block are consistent with the report and with the established process.

### Q4: Are reserve candidates ranked honestly?

Yes.

- **Triangle** (`0.9874x` geomean, reserve): M19 already accepted a strict focused probe
  for triangle. The existing probe narrows but does not exhaust the Triangle work surface,
  so it remains valid if the RTNN bridge fails. The reasoning "not the cleanest next
  no-POD bridge" because an M19 probe already exists is accurate.

- **RTDBSCAN** (`0.9881x` geomean, reserve): M40 gives component-union focused POD
  evidence. M35 identifies the grouped-union pass as the real bottleneck, and M43
  confirms the CuPy warp kernel clears the CPU-hot inversion locally. RTDBSCAN is a
  legitimate reserve candidate, but the M35 gap analysis correctly identifies that the
  bridge audit for RTNN presents a cleaner local-only work unit without reopening the
  grouped-union bottleneck.

Neither reserve candidate should preempt the RTNN bridge audit. The ranking is honest.

### Q5: Are stop conditions sufficient?

The four stop conditions cover the primary failure modes:

1. Repeat50 amortization without all-app shape bridge — correctly stops pure
   amortization claims.
2. App-specific RTNN shortcuts — correctly prevents regression to app-tuning.
3. No productized ranked-summary helper in source — correctly fails closed if the
   surface has drifted.
4. M69 cannot define same-contract focused evidence before POD — correctly gates POD
   commitment behind evidence definition.

The conditions are sufficient to prevent the main errors. The P2 gap noted in Q2 (input-
packing phase attribution) is partially covered by stop condition 1 and by must-answer
question 4, but M69 should carry forward an explicit instruction: if the runner-wall
improvement is attributable entirely to input-packing consolidation with no compression
in the ranked-summary execution phase, that outcome must be recorded and does not
authorize a focused runbook.

### Q6: Are non-authorization boundaries complete?

Yes. The JSON `non_authorization` block contains all 12 required flags, all set to
false:

- `release_authorized: false`
- `all_app_run_authorized: false`
- `pod_authorized: false`
- `paid_pod_spend_authorized: false`
- `focused_pod_spend_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_v3_over_v2_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `paper_reproduction_claim_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `automatic_partner_selection_authorized: false`
- `route_specific_rtnn_app_tuning_authorized: false`
- `watch_row_closure_authorized: false`

The `all_non_authorization_flags_false: true` check passes. The non-authorization
boundaries are complete and match the call for review.

## Failed Checks

None. The packet reports `failed_checks: 0`. All 18 check fields in the JSON are true.
Independent verification of key checks:

- `selected_family_is_set_a: true` — confirmed from frozen scorecard
  (`rtnn` row label: `architecture_bearing`, set: `A`)
- `selected_family_below_app_win_threshold: true` — confirmed: `1.0033x < 1.05x`
- `selected_family_not_severe_regression: true` — confirmed: `1.0033x > 0.90x` floor
- `selected_has_productized_helper: true` — confirmed: `run_fixed_radius_ranked_summary_3d_prepared_session` exists per M30-M34 ledger
- `selected_helper_has_generic_contract: true` — confirmed: helper body has no RTNN name per JSON `helper_body_has_no_rtnn_name: true`
- `m66_blocks_repeat_topology_stream_pod: true` — confirmed from M66 3-AI consensus
- `m67_accepts_barnes_hut_as_existing_material_family: true` — confirmed from M67 3-AI consensus

## Findings Summary

| Priority | Finding | Disposition |
|---|---|---|
| P2 | M69 should explicitly separate input-packing time savings from ranked-summary execution phase compression when attributing runner-wall improvement | Carry forward to M69 framing — not a blocker |
| P2 | A fifth stop condition — "if runner-wall improvement is sourced entirely from input-packing consolidation with no ranked-summary phase compression, stop before runbook" — would strengthen M69 | Carry forward to M69 — not a blocker |

No P1 issues. No blocking issues.

## Carry-Forward to M69

1. When mapping the `1.370176x` runner-wall signal to all-app shapes, explicitly
   separate input-packing time (`input_load_pack_sec`) from ranked-summary execution
   time (`runner_after_input_load_pack_sec`). The bridge audit should report which
   component drives the wall-time improvement.
2. Record a phase-attribution fact in the M69 output: if the runner-wall win is
   primarily from packing, document that finding rather than attributing it to the
   ranked-summary runner phase.
3. Do not interpret any M69 local shape bridge finding as POD authorization, runbook
   authorization, or all-app authorization. M69 is a local no-POD audit only.

## Verdict

`accept_m68_select_rtnn_ranked_summary_for_m69_local_audit_no_pod_no_release`

M68 correctly selects `fixed_radius_ranked_summary_3d_prepared_session` / RTNN as the
next generic Set-A family for a local no-POD phase/shape bridge audit. The exclusions
are consistent with M67 and M66 prior consensus. The repeat50 evidence boundary is
preserved. The M69 scope is appropriately staged. The reserve candidates are ranked
honestly. The stop conditions are adequate. The non-authorization boundaries are
complete.

## Non-Authorization

This review does not authorize:

- no V3 release
- no all-app benchmark run
- no POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no RT-core speedup claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure
