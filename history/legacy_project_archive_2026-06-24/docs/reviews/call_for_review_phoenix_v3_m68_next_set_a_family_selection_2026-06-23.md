# Call For Review: Phoenix V3 M68 Next Set-A Family Selection

Status:
`request_external_review_m68_next_set_a_family_selection_no_pod_no_release`

Please critically review the M68 next-family selection packet:

- Report:
  `docs/reports/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.json`
- Current handoff:
  `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`
- Frozen Set-A/B scorecard:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- M67 Barnes-Hut consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_3ai_consensus_2026-06-23.md`
- M66 topology-stream non-go consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md`
- RTNN repeat50 productized-runner evidence:
  `docs/rebuild/v3/phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md`

## Proposed Decision

M68 selects:

```text
fixed_radius_ranked_summary_3d_prepared_session
```

as the next generic Set-A family for M69 local no-POD phase/shape bridge audit.
The pressure app is RTNN, but the selected mechanism is the generic ranked-
summary prepared-session runner.

## Review Questions

1. Is RTNN fixed-radius ranked-summary the right next generic Set-A family after
   M67, given that Barnes-Hut is already internally counted, Spatial/RayJoin is
   M66 non-go, LibRTS is Set-B control work, and Hausdorff is already above the
   app-win threshold?
2. Does M68 correctly preserve the boundary that RTNN's existing `1.370176x`
   runner-wall signal is repeat50 focused evidence, not a single-shot,
   whole-RTNN, public speedup, or broad V3-over-V2 claim?
3. Is the proposed M69 scope correct: local phase/shape bridge audit first,
   before any runbook, POD request, all-app run, or release wording?
4. Are the reserve candidates ranked honestly: Triangle and RTDBSCAN remain
   valid later candidates, but should not preempt the RTNN bridge audit now?
5. Are the stop conditions sufficient to prevent app-specific RTNN tuning and
   repeat50 overclaiming?
6. Are the non-authorization boundaries complete?

## Requested Verdict Labels

Use exactly one:

- `accept_m68_select_rtnn_ranked_summary_for_m69_local_audit_no_pod_no_release`
- `accept_m68_selection_shape_but_change_next_family_before_m69`
- `blocked_m68_needs_local_fix_before_next_family_decision`
- `reject_m68_selection_repeats_leaf_first_error`

## Non-Authorization

This review request does not authorize:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no RT-core speedup claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure
