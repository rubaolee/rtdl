# Call For Review: Phoenix V3 M67 Barnes-Hut Phase-Structure Pre-Audit

Status:
`request_external_review_m67_barnes_hut_phase_structure_pre_audit_no_pod_no_release`

Please critically review the M67 local pre-audit packet:

- Report:
  `docs/reports/phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.json`
- Main prior evidence:
  `docs/reports/phoenix_v3_step1_barnes_hut_runner_parity_pod_ab_2026-06-22.md`
- M29 surface classification:
  `docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md`
- M45 blocker re-audit:
  `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- M66 redirect consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md`

## Review Questions

1. Does M67 correctly reconcile M45 and M66, or is it incorrectly reopening
   Barnes-Hut work that M45 already closed?
2. Is the phase-structure reading correct: historical prepared
   OptiX/frontier is a material predecessor-displacement reference, while the
   current fused Numba CUDA control has no new compressible phase for the
   runner to remove?
3. Is it valid to say the productized runner preserves the current fused
   control at parity (`0.999328x` geomean) without claiming the wrapper itself
   is faster?
4. Given M29 (`v2_14_has_cpu_fused_or_typed_stream_only`), is Barnes-Hut a
   V3 capability/productized-runtime addition rather than a same-contract
   V3-over-v2.14 speedup row?
5. Should Barnes-Hut be counted as an existing Step-1 material family after
   review, or should Phoenix V3 select a different Set-A family instead?
6. Are the non-authorization boundaries complete?

## Requested Verdict Labels

Use exactly one:

- `accept_m67_count_barnes_hut_as_existing_step1_material_family_no_pod_no_release`
- `accept_m67_pre_audit_but_do_not_count_barnes_hut_select_next_family`
- `blocked_m67_needs_local_fix_before_decision`
- `reject_m67_barnes_hut_reopened_wrong_path`

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
- no RT-core speedup claim for the Numba CUDA fused route
- no true-zero-copy claim
- no automatic partner selection
- no app-specific Barnes-Hut engine tuning
- no watch-row closure
