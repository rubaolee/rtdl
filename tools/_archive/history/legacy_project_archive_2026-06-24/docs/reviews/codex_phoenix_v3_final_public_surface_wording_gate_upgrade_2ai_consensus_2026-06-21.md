# Codex Consensus: Phoenix V3 Final Public-Surface Wording Gate Upgrade

Date: 2026-06-21

External review:

```text
docs/reviews/claude_phoenix_v3_final_public_surface_wording_gate_upgrade_review_2026-06-21.md
```

Consensus status:
`claude_codex_consensus_final_public_surface_wording_gate_upgrade_complete_not_release`

Verdict:
`approve-with-amendments-complete`

## Decision

Codex accepts Claude's focused review. The Phoenix V3 wording gate upgrade is
accepted as a final public-surface claim-boundary gate after the required P1
documentation corrections.

The gate now records:

```text
gate_level: final_public_surface_claim_boundary_gate
final_public_surface_gate: true
missing_expected_m7_row_ids: []
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

This closes the old "first-pass wording scanner only" ambiguity as a
claim-boundary-control issue. It does not authorize V3 release.

## Claude Findings And Resolution

Claude verdict: `approve-with-amendments`.

P0 findings: none.

P1-1 was fixed:

```text
docs/rebuild/v3/v3_current_status_2026-06-20.md
```

The stale six-row "Current Blocker" wording now records eleven exact
row-scoped M7-qualified rows and includes the grouped device-column rows, AABB
native query-handle rows, and RTNN prepared repeat50 row.

P1-2 was fixed:

```text
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
```

The stale ten-row M7-classification summary now records eleven rows and names
`rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`.

No gate-code change was required after Claude review.

## Validation

Focused gates and tests after P1 fixes:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
status: pass
final_public_surface_gate: true
missing_expected_m7_row_ids: []
violations: []

py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty
status: blocked_not_release
failed_checks: []

py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test
Ran 23 tests OK
```

Full Phoenix V3 rebuild after P1 fixes:

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
91 modules / 438 tests OK
```

## Claim Boundary

Allowed:

- The V3 public-surface wording gate is final for the current scanned
  claim-boundary surface.
- It verifies all eleven exact M7 row ids are visible.
- It fails on unsupported release, public speedup, broad V3-over-V2,
  package-install, multi-GPU portability, secondary-RT performance, and
  post-M150 leakage wording.

Forbidden:

- Do not say this authorizes release.
- Do not say broad V3-over-V2 speedup is authorized.
- Do not say package-install, multi-GPU portability, or secondary-RT
  performance confirmation is authorized.
- Do not say the eleven exact row-scoped claims are enough for a major release.

## Goal-Level Decision Self-Audit

Decision: accept the wording-gate upgrade after Claude P1 amendments, while
keeping Phoenix V3 blocked under aggregate release-readiness consensus.

1. Was I foolish?
   No. I sought external review, applied the stale-count fixes, reran the
   focused and full V3 rebuild gates, and kept release authorization false.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would have been to treat a green wording
   gate as release authorization or to ignore Claude's stale-count findings.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could have left the gate as "first-pass" and kept it as a blocker,
   but that would preserve an avoidable process ambiguity rather than solve it.
4. Can I now try a different path that actually solves the problem?
   Yes. With the final public-surface wording gate reviewed and machine-read,
   the remaining release blockers are narrowed to release authorization, the
   narrow eleven-row surface, and aggregate not-ready consensus.

