I have everything I need. Let me write the review now.

---

# Claude Compact Review: Phoenix V3 Twelve-Row Release Readiness After P1 Fixes

**Reviewer:** Claude Sonnet 4.6 (external, local Windows Claude Code)
**Date:** 2026-06-21
**Prior review (P1-fixed):** `docs/reviews/claude_phoenix_v3_twelve_row_p1_fixed_release_readiness_review_2026-06-21.md`
**Original prior review:** `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`

---

## Verdict: `approve-blocked-not-release`

No new P0 findings. P1-4 is fully closed. P1-1 is mechanically closed with one residual P1 item that must be resolved inside the Codex twelve-row consensus, not by further gate edits. Release remains blocked through four independently sufficient blockers. No new gate holes found.

---

## Q1 - Are P1-1 and P1-4 fixed?

### P1-4 (13.591x Barnes-Hut overclaim scanner): **Fully fixed.**

I read `scripts/v3_release_wording_gate.py` directly. Lines 218-230 confirm:

```python
BARNES_HUT_SUPPORTING_RATIO_PATTERN = re.compile(r"\b13\.591x\b", re.IGNORECASE)
BARNES_HUT_SUPPORTING_RATIO_ALLOWED_CONTEXT = (
    "supporting metadata", "supporting no-go", "metadata only",
    "not primary", "no-go", "forbidden", "forbidden shortcut",
    "rejected", "do not",
)
```

The scanner fires on any occurrence of `13.591x` outside `docs/reviews/` and fails the gate unless a 10-line context window contains an allowed phrase. The compact evidence confirms the Barnes-Hut candidate document reads "supporting no-go metadata only, not the primary claim" - which matches `"no-go"` in the allowed context. The wording gate reports 0 violations. P1-4 is closed with no residual.

### P1-1 (install gate scope eleven_row -> twelve_row): **Mechanically fixed, one residual P1 not yet closed.**

The compact evidence confirms all of the following were updated: install gate constant, release gate, runbook, status docs, tests. The gate output correctly shows:

```text
release_scope: source_tree_pod_gated_twelve_row
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
general_release_installer_ready: false
package_install_claim_authorized: false
release_authorized: false
```

**Residual P1 (carried from the P1-fixed review, still open):** The Codex scoped-wording consensus (`codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md`) was written for `source_tree_pod_gated_eleven_row` and authorized `installer_closes_release_blocker: true` only under that scope. Neither that consensus nor its Claude counterpart was re-reviewed after the candidate was updated to twelve_row. The wording gate's `REQUIRED_STRINGS` check validates against the updated candidate document - not against the consensus - so the gate passes while the underlying authorization gap remains.

This does not create a false release path: `release_authorized` is false through three independent channels beyond the install gate. But the residual is real and must be closed inside the Codex twelve-row consensus (see Q3). No further gate edits are required; the consensus wording is the fix.

---

## Q2 - Is `blocked_not_release` still the correct status?

**Yes.** All four blocking reasons are valid and independently sufficient:

| Blocking reason | Assessment |
|---|---|
| `release_authorization_false` | Hardcoded `false` in the gate; no document in the evidence chain authorizes release. |
| `twelve_row_surface_still_too_narrow_for_major_release` | 8 of 9 required capability families. Minimum for major release is 9. Not waivable. |
| `missing_point_location_topology_stream_m7_capability_family` | Spatial P0 was closed as `current_v3_future_research`, not as a promotion. Zero M7 rows in this family. Engine queue has no promotable items. |
| `twelve_row_release_readiness_consensus_missing` | Most recent aggregate consensus covered eleven rows and returned `not-release-ready-fix-p0`. No twelve-row aggregate consensus exists yet. |

The compact evidence also confirms:

```text
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
multi_gpu_performance_portability_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
```

All flags are correctly false. `blocked_not_release` is honest, sufficient, and not unduly conservative - it states the exact state of the evidence.

---

## Q3 - Should Codex write the consensus as `twelve_row_release_readiness_consensus_blocks_release`?

**Yes.** Once the consensus exists, the blocker label transitions from `twelve_row_release_readiness_consensus_missing` to `twelve_row_release_readiness_consensus_blocks_release`. The release gate picks up this rename correctly; `release_authorized` remains false regardless.

The Codex consensus must explicitly include all of the following to be acceptable:

1. **Confirm all four blocking reasons remain valid** under twelve-row scope.
2. **Resolve the installer-scope P1-new:** The twelfth row (Barnes-Hut fused-partner, `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`) uses Numba CUDA on the same RTX 4000 Ada pod with the same GPU Python package set as the eleven prior rows. The Codex consensus must state either: *(a)* `source_tree_pod_gated_twelve_row` is accepted as the correct successor to `source_tree_pod_gated_eleven_row` and the installer-blocker closure is confirmed under the updated scope; or *(b)* a fresh scoped-wording review is required before the twelve_row scope is confirmed.
3. **Confirm the Barnes-Hut row opens no new broad claims:** no RT-core claim, no whole-app claim, no broad V3-over-V2 claim. The 13.591x figure is supporting no-go metadata only.
4. **Record the following flags explicitly:**

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
twelve_row_release_readiness_consensus_blocks_release
```

A consensus that omits item 2 above is incomplete and does not close the P1-new.

---

## Q4 - Remaining P0/P1 issues in the compact evidence summary

**P0 findings: None.**

The gate machinery is internally consistent. All release-authorization flags are false. The wording gate passes with zero violations. The row IDs in `EXPECTED_ROW_SCOPED_M7_IDS` match the twelve rows listed in the compact evidence exactly. No structural hole allows a release-authorized path through the current gates.

**P1 items:**

| ID | Status | Resolution path |
|---|---|---|
| P1-new (installer-scope carry-over) | **Open** | Must be addressed in Codex twelve-row consensus - not a gate edit |
| P1-2 (external review for app catalog, backend maturity, performance model) | **Carryover, open** | Blocks future release authorization; does not block current Codex consensus |
| P1-3 (tutorial surface 07-15 coherence for release review) | **Carryover, open** | Same |
| P1-5 (negative-row wording 0.065x / 0.034x placement) | **Carryover, open** | Same |

None of P1-2, P1-3, or P1-5 block the Codex twelve-row consensus from being written. P1-new must be addressed **in** the consensus, not before it.

**One structural observation (not a new finding, confirmation of prior review):** The `REQUIRED_STRINGS` check in the wording gate validates the updated candidate document for the twelve_row scope label, not the Codex consensus document. This design gap was already identified in the P1-fixed review. It is tolerable under the current blocked status because the P1-new forces the consensus to close it explicitly. If release authorization were ever being considered, this would need to be a gate check rather than a prose requirement.

---

## Q5 - Verdict

```text
approve-blocked-not-release
```

P1-1 and P1-4 are fixed in the ways claimed. The gate machinery is self-consistent and internally honest. All blocking reasons are correctly named, independently sufficient, and not contradicted by any evidence in the compact summary. No P0 holes were found. The residual P1-new (installer-scope carry-over) must be resolved in the Codex twelve-row consensus; it does not require further gate changes and does not change the blocked status.

**This review does not authorize release. It authorizes Codex to write the twelve-row aggregate consensus.**

---

## Required Codex Consensus Checklist (non-negotiable items)

- [ ] `twelve_row_release_readiness_consensus_blocks_release` as explicit status string
- [ ] All four blocking reasons confirmed as valid under twelve-row scope
- [ ] Installer-scope P1-new explicitly resolved (confirmation or re-review requirement)
- [ ] Barnes-Hut row confirmed as opening no new broad/RT-core/whole-app claims
- [ ] `release_authorized: false`
- [ ] `public_speedup_claim_authorized: false`
- [ ] `broad_v3_faster_than_v2_claim_authorized: false`
