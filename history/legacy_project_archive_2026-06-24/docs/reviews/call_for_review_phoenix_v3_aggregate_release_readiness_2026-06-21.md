# Call For Review: Phoenix V3 Aggregate Release Readiness

Date: 2026-06-21

Please critically review whether Phoenix V3 is now responsible to release under
the narrow current scope, or whether it must remain blocked.

This is an aggregate review after two scoped blocker closures:

1. source-tree/pod-gated installer closure under `source_tree_pod_gated_eleven_row`;
2. secondary hardware blocker closure by Claude/Codex-reviewed single-RTX
   hardware-scope waiver under
   `single_rtx_4000_ada_driver_550_127_05_pod`.

Do not assume broad V3 release readiness. The current gate still says
`blocked_not_release`.

## Files To Read

Primary gate snapshots:

```text
docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_install_reproducibility_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_secondary_platform_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json
```

Current status and blocker docs:

```text
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md
docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md
docs/rebuild/v3/v3_secondary_platform_strategy_2026-06-21.md
docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md
```

Release-surface evidence:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md
```

Existing release-readiness reviews:

```text
docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md
docs/reviews/claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_2ai_consensus_2026-06-21.md
docs/reviews/claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md
docs/reviews/claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md
```

Public docs to spot-check:

```text
README.md
docs/README.md
docs/learn/current_claim_boundaries.md
docs/app_engine_support_matrix.md
docs/application_catalog.md
docs/backend_maturity.md
docs/performance_model.md
tutorials/current/README.md
```

Local validation just run by Codex:

```text
py -3 scripts/v3_release_wording_gate.py --pretty --json-out docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json
py -3 scripts/v3_phoenix_release_readiness_gate.py --pretty --json-out docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json
py -3 scripts/run_test_matrix.py --group v3_rebuild
```

The full matrix reported 91 modules / 438 tests OK.

## Current Machine Facts

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
package_install_claim_authorized: false
multi_gpu_performance_portability_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
release_scope: source_tree_pod_gated_eleven_row
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
generic_engine_work_queue_closed_not_release
current_m7_qualified_release_rows: 11
```

Current release gate blockers:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
broad_v3_faster_than_v2_claim_not_authorized
current_eleven_row_release_readiness_consensus_blocks_release
```

## Review Questions

1. After the scoped installer closure and the Claude/Codex hardware-scope
   waiver, is Phoenix V3 now responsible to release under the exact
   `source_tree_pod_gated_eleven_row` and
   `single_rtx_4000_ada_driver_550_127_05_pod` scopes?
2. If not, which P0 blockers remain real, and which ones are stale and should
   be removed from the gate?
3. Is the eleven-row current surface enough for a major V3 release if the docs
   clearly avoid broad V3-over-V2, package-install, multi-GPU portability, and
   general app acceleration claims?
4. Are the public docs and tutorials likely to mislead users about performance,
   hardware portability, installer readiness, V2-vs-V3 speedup, or whole-app
   acceleration?
5. What exact gate/doc/test amendments are required before release can be
   authorized, if any?

Please write the review to:

```text
docs/reviews/claude_phoenix_v3_aggregate_release_readiness_review_2026-06-21.md
```

Use one of these verdicts:

- `release-ready-source-tree-eleven-row-scoped`
- `not-release-ready-fix-p0`
- `reject-overclaim`

If you choose release-ready, list the exact allowed claims and the exact claims
that must remain forbidden. If you choose not-release-ready, list only the P0
items that truly block the scoped release.

## Goal-Level Decision Self-Audit

1. Was I foolish?

No. Requesting this review is the necessary next step after scoped installer
and scoped hardware-waiver closure; it avoids self-authorizing release.

2. If yes, what actions made the decision foolish?

Not applicable. The foolish action would be turning green structural gates into
release authorization without external review.

3. Was there another path that would have avoided getting stuck on that idea?

Yes. Continue generic-engine tuning indefinitely, but the current queue says no
existing evidence is promotable now and no active generic-engine P0 remains.

4. Can I now try a different path that actually solves the problem?

Yes. Ask for an aggregate external review that decides whether the current
narrow V3 is release-ready or names the remaining P0 blockers precisely.
