# Phoenix V3 Aggregate Release-Readiness Review Request: 13-Row Surface

Reviewer: Claude preferred; Gemini if Claude is unavailable.
Date: 2026-06-22

## Post-Review Synchronization Note

This request remains the historical aggregate 13-row review packet. The current
gate has since been synchronized with Claude's later core-gap verdict:

```text
core_gaps_external_verdict: approve_blocked_not_release
core_gaps_external_status_line: external_verdict_obtained_claude_approve_blocked_not_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
set_a_set_b_release_bar_proposal_status: proposal_only_not_authorization
```

Use this packet as scoped 13-row evidence only. It is not current V3 release
authorization and it does not override the major-version performance mandate.

## Question

Please review the current Phoenix V3 release-readiness state and decide whether
the 13-row / 9-capability surface is now ready for a responsible user-facing V3
release, or whether release must remain blocked.

This is an aggregate release-readiness review, not a row-level review.

## Current Machine State

Primary current gate:

`docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`

Legacy aggregate alias, regenerated to the same current state:

`docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json`

Current gate facts:

- `status: redo_required`
- `m7_qualified_release_rows: 13`
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_v3_faster_than_v2_claim_authorized: false`
- `blocking_reasons: ["broad_v2x_performance_not_proven", "serious_all_app_paired_evidence_failed_release_bar", "current_scoped_13_row_surface_not_v3_major_release", "current_core_gap_external_review_blocks_release"]`
- release-surface rows: 13
- planned capability families: 9/9
- missing capability families: none
- current review-packet reference files: 23
- surface row integrity rows: 13
- surface row paths all exist: true
- surface row unsupported-claim flags blocked: true
- surface rows are generic capability rows: true

## Installer Scope Closure

The old twelve-row installer/reproducibility scope mismatch has been superseded.
The current installer/reproducibility gate records:

- `release_scope: source_tree_pod_gated_thirteen_row`
- `installer_closes_release_blocker: true`
- `installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row`
- `source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true`
- `aggregate_13_row_installer_scope_review_required: false`
- `staged_gpu_pod_gate_available: true`
- `general_release_installer_ready: false`
- `package_install_claim_authorized: false`
- `release_authorized: false`

The scope-extension evidence is:

- `docs/rebuild/v3/v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_2ai_consensus_2026-06-22.md`

Important boundary: this closes only the source-tree/pod-gated thirteen-row
installer blocker. It does not make the staged script a general package
installer and does not authorize package-install wording.

## Why This Review Exists

The previous aggregate release-readiness consensus was based on a 12-row surface
and still had a missing Spatial topology-stream capability-family blocker. That
historical gap is now closed by one bounded Spatial supplemental row:

`point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`

Its boundary is documented in:

- `docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json`

The current release-surface breadth gate now records thirteen exact
M7/supplemental rows, 9/9 planned capability families, and no missing capability
families. It also records a 13-row integrity manifest tying every current
surface row to existing evidence/review/consensus paths, blocked unsupported
claim flags, and a planned generic capability family.

## Evidence To Inspect

Core gates:

- `scripts/v3_phoenix_release_readiness_gate.py`
- `scripts/v3_phoenix_release_surface_breadth_gate.py`
- `scripts/v3_phoenix_objective_conformance_gate.py`
- `scripts/v3_phoenix_release_gap_ledger.py`
- `scripts/v3_phoenix_next_engine_work_queue.py`
- `scripts/v3_release_wording_gate.py`
- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `scripts/v3_phoenix_secondary_platform_gate.py`

Current artifacts:

- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_install_reproducibility_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_secondary_platform_gate_2026-06-21.json`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_release_completion_audit_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_user_facing_performance_dossier_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_objective_conformance_gate_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_release_gap_ledger_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json`
- `docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md`
- `docs/reports/phoenix_v3_surface_integrity_gate_update_2026-06-22.md`
- `docs/reports/phoenix_v3_short_user_path_guard_update_2026-06-22.md`

Historical blockers to compare:

- `docs/reviews/claude_phoenix_v3_aggregate_release_readiness_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_aggregate_release_readiness_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_compact_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_2ai_consensus_2026-06-21.md`

## Verification Already Run

Focused current-surface checks:

```text
py -3 -m unittest tests.v3_phoenix_objective_conformance_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_user_facing_performance_dossier_test tests.v3_release_wording_gate_test
Ran 15 tests ... OK
```

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild --json-out docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json
111 modules / 557 tests OK
```

External-review process guard:

```text
one complete packet
one bounded automated attempt in the active work loop
no substantive verdict before timeout -> record external_review_not_obtained
no release promotion without a real external verdict
continue non-release V3 cleanup
```

Process authority:

`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`

## Required Review Questions

1. Does the 13-row / 9-capability surface remove the old surface-width and
   missing-Spatial blocker?
2. Does the reviewed `source_tree_pod_gated_thirteen_row` installer scope close
   the scoped installer/reproducibility blocker for the current release surface?
3. Are there remaining P0/P1 blockers that still prevent a responsible V3
   release?
4. If release should remain blocked, identify exact blockers and required fixes.
5. If release can be authorized, state exactly what wording/scope is authorized
   and what remains forbidden.
6. Confirm whether package-install, hardware portability, broad V3-over-V2
   speedup, public Spatial speedup, RTDL-beats-RayJoin, true-zero-copy, C ABI /
   embedding, and whole-app claims remain forbidden.

## Expected Output Format

The first lines of the review response must be machine-readable by
`scripts/v3_phoenix_external_verdict_intake.py`:

```text
Reviewer: Claude
Verdict: `approve_blocked_not_release`
Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.
```

Use `Reviewer: Claude`, `Reviewer: Gemini`, or
`Reviewer: Human external reviewer`.

Use exactly one `Verdict:` label:

- `release_ready`
- `approve_blocked_not_release`
- `block_p0`
- `block_p1`

The reusable response template is:

`docs/reviews/phoenix_v3_external_verdict_response_template_2026-06-22.md`

After the machine-readable header, include:

- Findings ordered by severity.
- Required fixes before release, if any.
- Exact release authorization statement.
- Exact non-authorized claim boundaries.

## Goal-Level Decision Audit

1. Was I foolish? No. The review request now reflects the current 13-row
   installer-reviewed state instead of asking Claude to review a stale twelve-row
   mismatch.
2. If yes, what actions made the decision foolish? It would be foolish to claim
   release from green tests alone, or to leave stale installer mismatch wording
   in the aggregate review packet.
3. Was there another path? Yes. I could have sent the old packet and forced
   Claude to rediscover the already-closed scope issue, but that wastes review
   bandwidth.
4. Can I now try a different path? Yes. Ask for a direct release-readiness
   judgment on the actual current evidence and keep all release/public speed
   flags false unless the review explicitly authorizes them.


