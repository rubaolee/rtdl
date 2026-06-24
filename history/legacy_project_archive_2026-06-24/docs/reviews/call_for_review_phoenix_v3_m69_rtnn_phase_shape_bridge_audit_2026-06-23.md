# Call For Review: Phoenix V3 M69 RTNN Phase/Shape Bridge Audit

Status:
`request_external_review_m69_rtnn_phase_shape_bridge_audit_no_pod_no_release`

Please critically review the M69 local RTNN phase/shape bridge audit:

- Report:
  `docs/reports/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.json`
- M68 consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m68_next_set_a_family_selection_3ai_consensus_2026-06-23.md`
- Frozen Set-A/B scorecard:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- RTNN repeat50 evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json`
- RTNN app source:
  `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- Prepared execution source:
  `src/rtdsl/prepared_execution.py`

## Proposed Decision

M69 says RTNN is:

```text
bridgeable_but_not_runbook_authorized
```

The existing RTNN repeat50 evidence is not hot-query speedup and not a
whole-app claim. It is a phase-split runner-wall signal:

- runner-wall delta: `0.866893s`
- input load/pack share: `0.323`
- runner-after-pack share: `0.677`
- hot-query speedup vs legacy: `0.988781x`

The frozen RTNN all-app scorecard still shows a real app-win gap:

- RTNN all-app rows: `14`
- rows below `1.05x`: `13`
- shape groups below `1.05x`: `6`

## Review Questions

1. Is M69 correct that RTNN is bridgeable to the generic
   `fixed_radius_ranked_summary_3d_prepared_session` runner surface?
2. Is the phase attribution correct and sufficiently honest: input load/pack is
   about `32.3%` of the runner-wall delta, runner-after-pack is about `67.7%`,
   and hot-query speedup is not the material source?
3. Does M69 correctly identify that the current front door uses
   `prepared_optix_ranked_summary`, while the productized runner mode exists
   separately as `prepared_execution_ranked_summary`?
4. Is the next recommendation right: M70 may draft a reviewed focused protocol
   with no execution, but M69 itself authorizes no runbook, no POD, no all-app,
   and no public claims?
5. Are the stop conditions sufficient to prevent RTNN app-specific tuning,
   repeat50 overclaiming, and mixing exact aggregate / productized runner /
   graph partner bridge contracts into one public claim?
6. Are the non-authorization boundaries complete?

## Requested Verdict Labels

Use exactly one:

- `accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release`
- `accept_m69_bridge_shape_but_select_reserve_candidate_before_m70`
- `blocked_m69_needs_local_fix_before_bridge_decision`
- `reject_m69_rtnn_not_bridgeable_repeats_leaf_first_error`

## Non-Authorization

This review request does not authorize:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no runbook execution
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no RT-core speedup claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure
