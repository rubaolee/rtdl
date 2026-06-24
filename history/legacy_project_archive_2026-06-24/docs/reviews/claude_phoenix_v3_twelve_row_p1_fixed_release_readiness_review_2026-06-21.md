# Claude Review: Phoenix V3 Twelve-Row Release Readiness After P1 Fixes

Reviewer: Claude Sonnet 4.6 (external, local Windows Claude Code)
Date: 2026-06-21
Prior review:
`docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`
Supersedes: prior review for the purpose of the Codex twelve-row consensus.

---

## Verdict: `approve-blocked-not-release`

Release remains blocked. The P1-4 fix is complete. The P1-1 fix is partially
complete with one new P1 inconsistency that the fresh twelve-row Codex consensus
must explicitly address. No new P0 findings.

---

## Direct Answers to the Five Review Questions

### Q1 — Are P1-1 and P1-4 actually fixed?

**P1-4 (Barnes-Hut 13.591x overclaim scanner): Fixed.**

`v3_release_wording_gate.py` now contains:

```python
BARNES_HUT_SUPPORTING_RATIO_PATTERN = re.compile(r"\b13\.591x\b", re.IGNORECASE)
BARNES_HUT_SUPPORTING_RATIO_ALLOWED_CONTEXT = (
    "supporting metadata", "supporting no-go", "metadata only",
    "not primary", "no-go", "forbidden", "forbidden shortcut",
    "rejected", "do not",
)
```

The pattern fires on any `13.591x` occurrence in non-review files and fails the
gate unless surrounding context (10 lines) contains an allowed phrase. The
Barnes-Hut candidate document (`phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md`)
is in `DEFAULT_FILES` and the 131,072-body row entry reads: "The 13.591x
comparison against the current prepared RTDL/OptiX frontier-emission route is
supporting no-go metadata only, not the primary claim." That passes the context
check. The wording gate currently reports:

```text
gate_level: final_public_surface_claim_boundary_gate
final_public_surface_gate: true
missing_expected_m7_row_ids: []
violations: []
release_authorized: false
```

P1-4 is fully closed.

**P1-1 (install gate scope from eleven_row to twelve_row): Partially fixed.**

What was done correctly:

- `SCOPED_RELEASE_SCOPE` constant in `v3_phoenix_install_reproducibility_gate.py`
  changed to `"source_tree_pod_gated_twelve_row"`.
- `v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`
  updated to read `release_scope: source_tree_pod_gated_twelve_row` and
  `installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row`.
- Install gate output now correctly reports both fields as `twelve_row`.
- `v3_install_reproducibility_strategy_2026-06-21.md` updated to reference
  `twelve_row` scope.
- `v3_release_authorization_blockers_2026-06-20.md` updated with `twelve_row`
  phrases (gate check `blockers_cover_release_reasons: true` passes).
- Gate test confirms twelve_row output.

**New P1 finding — installer-closure scope was never re-reviewed for twelve_row:**

The Codex scoped-wording consensus
(`codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md`)
explicitly records:

```text
release_scope: source_tree_pod_gated_eleven_row
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
```

It authorized `installer_closes_release_blocker: true` **only for eleven_row
scope**. The associated Claude review
(`claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md`)
evaluated `source_tree_pod_gated_eleven_row` throughout. Neither document was
re-run after the candidate was updated to twelve_row.

The gate's `REQUIRED_SCOPED_WORDING_CODEX_CONSENSUS_PHRASES` still checks for
`"release_scope: source_tree_pod_gated_eleven_row"` in the consensus doc — and
that check passes — which means the gate is validating an eleven_row consensus
while claiming twelve_row scope.

The effect: the gate output says `installer_closes_release_blocker: true` under
`source_tree_pod_gated_twelve_row` scope, but the only Codex consensus that ever
approved `installer_closes_release_blocker: true` did so for eleven_row. The
twelve_row scope update was not independently reviewed.

Severity: **P1.** This does not create a false path to release — `release_authorized`
remains false through multiple independent blockers, and the
`twelve_row_release_readiness_consensus_missing` blocker explicitly captures
the need for a fresh aggregate consensus. However, the fresh twelve-row Codex
consensus MUST explicitly address whether the installer-blocker closure carries
over from eleven_row to twelve_row, and if so confirm this is appropriate.

Suggested Codex consensus wording:

> The Barnes-Hut fused-partner row (row 12) uses the same RTX 4000 Ada pod
> environment and the same GPU Python package set as the eleven prior rows.
> The `source_tree_pod_gated_twelve_row` scope is accepted as the correct
> successor to `source_tree_pod_gated_eleven_row`; the installer-blocker closure
> is confirmed under the updated scope.

Without that explicit statement, the twelve_row scope for `installer_closes_release_blocker: true`
has no reviewed consensus basis.

### Q2 — Is the current `blocked_not_release` gate honest and sufficient after the fixes?

Yes. The gate reports:

```text
status: blocked_not_release
blocking_reasons:
- release_authorization_false
- twelve_row_surface_still_too_narrow_for_major_release
- missing_point_location_topology_stream_m7_capability_family
- twelve_row_release_readiness_consensus_missing
failed_checks: []
```

All four blocking reasons are correct and independently sufficient:

1. `release_authorization_false` — no authorization exists anywhere in the
   evidence chain; every document and gate checks as false.

2. `twelve_row_surface_still_too_narrow_for_major_release` — the surface breadth
   gate records 8 of 9 required capability families; the minimum for major
   release is 9; the gap is `point_location_topology_stream`; existing evidence
   is not promotable.

3. `missing_point_location_topology_stream_m7_capability_family` — the Spatial
   RayJoin P0 was closed as `spatial_active_p0_closed_current_v3_future_research`,
   not as a promotion. No M7-qualified row exists in this family.

4. `twelve_row_release_readiness_consensus_missing` — the most recent aggregate
   release-readiness consensus was for eleven rows and returned
   `not-release-ready-fix-p0`. No twelve-row aggregate consensus exists yet.
   This is the primary reason for the current review.

The `failed_checks: []` outcome is reliable. All structural checks across the
M7 packet, app boundary, wording gate, install gate, secondary platform gate,
surface breadth gate, and engine work queue pass. The empty failed-checks list
does not indicate release readiness; it indicates the gate machinery is
internally consistent.

The gate is also correctly conservative about the aggregate release consensus:
the `REQUIRED_AGGREGATE_RELEASE_CONSENSUS_PHRASES` check against
`codex_phoenix_v3_aggregate_release_readiness_2ai_consensus_2026-06-21.md` still
passes because that consensus contains `installer_closes_release_blocker_scope:
source_tree_pod_gated_eleven_row`. This means the blocking consensus-of-record
only knew about eleven rows and eleven_row scope. The fresh twelve-row consensus
will supersede it.

### Q3 — Should a Codex twelve-row consensus record `twelve_row_release_readiness_consensus_blocks_release`?

Yes. If the Codex consensus agrees release remains blocked (which it should,
given the missing `point_location_topology_stream` family and the installer-scope
P1 above), the consensus must use the status:

```text
twelve_row_release_readiness_consensus_blocks_release
```

This replaces `twelve_row_release_readiness_consensus_missing` in the release
readiness gate's blocker list. The Codex consensus must additionally:

- Explicitly confirm the four current blocking reasons remain valid.
- Explicitly address the installer-scope P1 (either confirming twelve_row scope
  is acceptable, or requiring a fresh scoped-wording review before it can be
  confirmed).
- Confirm that the Barnes-Hut fused-partner row does not open any new claims
  (no RT-core, no whole-app, no broad V3-over-V2).
- Record `release_authorized: false`, `public_speedup_claim_authorized: false`,
  and `broad_v3_faster_than_v2_claim_authorized: false`.

### Q4 — Are there remaining P0/P1 issues that would make status docs, gates, or the tutorial surface misleading?

**P0 findings: None.**

The blocking status is correct, all gate flags are false, the tutorial surface
does not claim release, and the wording gate catches overclaims.

**New P1 from this review:**

- P1-new: Installer-closure scope carries over from eleven_row to twelve_row
  without a reviewed Codex consensus for twelve_row. The fresh Codex twelve-row
  consensus must explicitly confirm or require re-review of this scope update.

**Carryover P1 items from the prior review (not all re-verified here):**

- P1-2: External review acceptance for app catalog
  (`docs/application_catalog.md`), backend maturity
  (`docs/backend_maturity.md`), and performance model
  (`docs/performance_model.md`) is noted as outstanding. These are not part of
  the current gate checks.

- P1-3: Reviewer acceptance that the tutorial surface (07–15) is coherent for
  a release review is noted as outstanding.

- P1-5: Final placement and reviewer acceptance of negative-row wording
  (0.065x / 0.034x) is noted as outstanding.

These carryover items do not block the current Codex twelve-row consensus from
being written, since they affect future release authorization, not the current
blocked status.

**Surface-level verification pass:**

- `v3_current_status_2026-06-20.md` correctly lists twelve rows and says
  `release_authorized: false` in all summary blocks. No misleading language
  found.
- Barnes-Hut fused-partner candidate correctly identifies the 13.591x figure as
  "supporting no-go metadata only, not the primary claim."
- The release surface breadth gate correctly records `m7_capability_family_count: 8`
  and `minimum_m7_capability_families_for_major_release: 9`.
- The surface breadth blocking reasons list is accurate and complete.

### Q5 — Verdict

```text
approve-blocked-not-release
```

---

## Summary for Codex Consensus Author

**State that must carry forward into the Codex consensus:**

```text
Phoenix M7-qualified release rows: 12
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
status: blocked_not_release
blocking_reasons:
  - release_authorization_false
  - twelve_row_surface_still_too_narrow_for_major_release
  - missing_point_location_topology_stream_m7_capability_family
  - twelve_row_release_readiness_consensus_blocks_release  (replaces _missing)
```

**New item the Codex consensus must resolve:**

P1-new: Confirm that the installer-blocker closure is accepted under
`source_tree_pod_gated_twelve_row` scope (the twelfth row uses the same pod
environment and GPU package set), or require a fresh scoped-wording review
before the twelve_row scope is confirmed.

**This review does not authorize release.**
