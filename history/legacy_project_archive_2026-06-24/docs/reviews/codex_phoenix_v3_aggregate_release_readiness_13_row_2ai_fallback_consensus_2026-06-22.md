# Codex Fallback Consensus: Phoenix V3 Aggregate 13-Row Release Readiness

Date: 2026-06-22

Status: `codex_subagent_fallback_consensus_approve_blocked_not_release`

This is a fallback Codex + Codex-subagent consensus because no Claude/Gemini
aggregate 13-row release-readiness verdict was obtained. It does not replace the
required external Claude/Gemini release authorization.

## Inputs

Review request:

`docs/reviews/call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md`

External-AI blocked record:

`docs/reviews/external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md`

Codex subagent review:

`docs/reviews/codex_subagent_phoenix_v3_aggregate_release_readiness_13_row_review_2026-06-22.md`

Current release-readiness gate:

`docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`

Current aggregate alias:

`docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json`

Current release-surface breadth gate:

`docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`

Completion audit:

`docs/rebuild/v3/phoenix_v3_release_completion_audit_2026-06-22.md`

User-facing performance dossier:

`docs/rebuild/v3/phoenix_v3_user_facing_performance_dossier_2026-06-22.md`

Full V3 rebuild evidence:

`docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json`

External-review process guard:

`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`

Short user-path guard:

`docs/reports/phoenix_v3_short_user_path_guard_update_2026-06-22.md`

## Consensus

1. The old missing-Spatial / surface-width blocker is removed.

The current surface has 13 total M7/supplemental rows, covers all 9 planned capability families, and records no missing capability families.

2. Phoenix V3 release remains blocked.

The live machine gate remains:

```text
status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
  - current_core_gap_external_review_blocks_release
```

3. The current green test matrix is necessary but not sufficient.

The latest recorded V3 rebuild matrix is green:

```text
111 modules / 557 tests OK
```

That evidence supports the current 13-row scoped surface. It does not authorize a major V3 release, broad V3-over-V2 speedup wording, public Spatial speedup wording, package-install readiness, broad hardware portability, or whole-app claims.

4. The scoped installer/reproducibility blocker is closed for the current
13-row source-tree/pod-gated surface.

The current installer/reproducibility closure is explicitly scoped to:

```text
source_tree_pod_gated_thirteen_row
```

Claude reviewed the scope-extension candidate, Codex recorded consensus, and
the gate now records:

```text
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
```

5. The current learner path is shorter and safer, but it is not release
authorization.

The public documentation map and `tutorials/current/README.md` now route users
through first run, hello world, backend choice, one benchmark row, and claim
boundaries before deeper evidence material. This improves user responsibility
for the current surface, but it does not authorize release wording.

This is not package-install readiness and does not authorize general installer
wording.

5. The next release-critical action is bounded external aggregate review.

Use the current 13-row packet as the external-review target, but do not wait on
Claude/Gemini indefinitely. Follow the bounded protocol:

```text
one complete packet
one bounded automated attempt in the active work loop
no substantive verdict before timeout -> record external_review_not_obtained
no release promotion without a real external verdict
continue non-release V3 cleanup
```

If Claude, Gemini, or a human reviewer authorizes the 13-row aggregate packet,
update and regenerate the release-readiness gate. Until then, keep release
blocked.

## Decision Audit

Decision: keep Phoenix V3 blocked after the 13-row / 9-capability surface until a fresh external aggregate release-readiness review explicitly authorizes release.

1. Was I foolish?

No for this decision. The stale missing-Spatial blocker was removed, but I did not let that become an unsupported release claim.

2. If yes, what actions made the decision foolish?

The foolish action would have been to treat a green matrix, a closed breadth gap, or a Codex-only fallback review as a user-facing major-release authorization.

3. Was there another path that avoided being trapped in one line of thought?

Yes. The better path is exactly the current one: separate row-scoped evidence from release authorization, remove stale blockers, and keep the aggregate release gate locked until external review is available.

4. Can I now try a different path that truly solves the problem?

Yes. The productive path is to use the current 13-row packet as the
external-review target, make only bounded external-review attempts, and only
then decide whether V3 can move from scoped evidence to responsible user-facing
release.

## Final Boundary

Current supportable statement:

Phoenix V3 has a 13-row, 9-capability row-scoped/supplemental M7 evidence surface, with the old missing-Spatial breadth gap closed. Phoenix V3 is not release-authorized yet.

Forbidden claims remain:

- release-ready V3
- broad V3 faster than V2.x
- public Spatial speedup
- RTDL beats RayJoin
- whole-app acceleration
- package-install readiness
- broad hardware portability
- true zero-copy
- V4/C ABI/embedding readiness

