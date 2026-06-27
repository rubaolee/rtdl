I have all four files. Writing the formal review now.

---

# Formal Review: V4 Goal4647 Partner Inventory Boundary Ledger

**Date:** 2026-06-25
**Reviewer:** Claude (Sonnet 4.6), one AI seat
**Verdict:** `accept_with_minor_edits`

---

## Verdict Rationale

Goal4647 is substantively complete and safe to proceed to Goal4648. The two required exit artifacts exist, AM1 is preserved everywhere it matters, and the ledger delivers exactly what AM5 requested — a thin inventory-plus-boundary-ledger rather than a standalone truth-freeze goal. No false claims, no unblocked CuPy performance language, no arbitrary Numba callback language, no Barnes-Hut promotion, no partner-migration-as-speed-win language. Two minor inconsistencies need a small correction before Goal4647 is marked formally closed; neither blocks Goal4648 execution.

---

## Mandatory Check Results

### Check 1 — Is Goal4647 complete enough to start Goal4648?

**Pass.**

Both required exit artifacts exist and are consistent with each other:
- `v4_goal4647_v2_14_partner_inventory_boundary_ledger_2026-06-25.md`
- `evidence/v4_goal4647_partner_inventory_2026-06-25.json`

The ledger names four concrete Goal4649 CuPy certification targets, one Goal4650 Numba surface, and two explicit `rejected_or_no_go` Barnes-Hut routes. Goal4648 has enough input to define contracts and numeric bars. Execution may begin on Goal4648 in parallel with closing the minor edits below.

---

### Check 2 — Does the ledger preserve AM1: partner migration is not a V4 speed win?

**Pass, fully preserved.**

AM1 appears in every layer:

- **Goal chain** (`v4_goals_4647_4658_revised…`), Binding Integrity Locks: "`formal_high_performance_v4_supported` cannot be triggered by `partner_migration` or `partner_parity` rows."
- **Ledger** (`v4_goal4647_v2_14_partner_inventory_boundary_ledger…`), Integrity Locks section: "Partner migration is not a V4 speed win. Partner parity is not a V4 speed win. Historical V2.14/V3 ratios may select candidates for rerun, but cannot become public V4 performance claims without a V4 run."
- **JSON**: `"partner_migration_counts_as_v4_speed_win": false`; every CuPy candidate row has `claim_class` containing `_not_v4_speed_win` and `public_claim_status` of `blocked_until_v4_cupy_rerun` or equivalent.
- **What This Does Not Authorize** section: explicitly lists "treating partner migration as V4 speed evidence."

The two `promotion_candidate_strong` rows are the ones most at risk of being misread. Both carry `claim_class: partner_migration_candidate_not_v4_speed_win` and `public_claim_status: blocked_until_v4_cupy_rerun`. The 100.019x and 174.645x vs Embree figures — which are striking — are correctly tagged as denominator-specific historical results, not V4 claims.

---

### Check 3 — Are the candidate classifications reasonable?

**Pass, with one minor framing inconsistency noted below.**

| Classification | Count | Assessment |
|---|---|---|
| `promotion_candidate_strong` | 2 | Reasonable. Two `cupy_grouped_reduction_device_columns` rows have documented multi-run V3 dossier ratios with explicit denominator and scale. "Strong" is appropriate given the consistency of the evidence. |
| `promotion_candidate_needs_rerun` | 5 | Reasonable. Each row lacks either a frozen V4 denominator, a certified V4 contract, or a known V4 front-door run. The `rtnn_prepared_ranked_summary_cupy_reference` row is notable: its historical denominator is the *CuPy* reference (i.e., RTDL beats CuPy at nearest-neighbor), not a V2.14 internal baseline — this is correctly left unblocked for future route binding rather than forced into a V4 speed claim. |
| `historical_only` | 3 | Reasonable. `v2_cupy_control_apps_rawkernel_large_scale` and `tier3_numba_ptx_spike` are correctly excluded from promotion. `numba_component_union_current_v4_surface` is the already-certified V4 surface — see **Minor Edit 1** below. |
| `rejected_or_no_go` | 2 | Correct. Both Barnes-Hut rows belong here. The Numba CUDA fused route is not RT-core and is app-specific; the OptiX+partner frontier route is slower than the fastest same-basis route. Neither belongs in V4.0 generic Tier-2 release wording. |

---

### Check 4 — Are CuPy claims still blocked until Goal4649 V4 rerun/certification?

**Pass, unambiguous.**

- JSON field: `"cupy_performance_claim_authorized": false`
- V4 Truth Ledger: "CuPy has strong V2/V3 historical evidence, but no V4-certified CuPy performance surface yet. `Blocked until Goal4649`."
- Every CuPy candidate row has `public_claim_status` set to `blocked_until_v4_cupy_rerun` or `blocked`.
- "What This Does Not Authorize" explicitly names CuPy performance claims.

---

### Check 5 — Are Numba claims limited to fixed continuations, with arbitrary callbacks still Tier-3 spike-only?

**Pass.**

- V4 Truth Ledger: "Fixed Numba continuation evidence exists; arbitrary Numba callback remains Tier-3 spike-only."
- `tier3_numba_ptx_spike` row: `claim_class: unsupported_callback_boundary`, `public_claim_status: blocked`, `promotion_needed: none in Goals4647-4658; keep blocked unless a future Tier-3 protocol passes`.
- JSON field: `"arbitrary_numba_callback_claim_authorized": false`
- "What This Does Not Authorize" explicitly names arbitrary Numba callback claims.

The PTX generation partial-success is accurately recorded as a negative/failed attempt (OptiX module link failed for bare helper PTX), not as support evidence.

---

### Check 6 — Are Barnes-Hut partner routes correctly kept as no-go/negative evidence for V4.0 generic Tier-2 release wording?

**Pass.**

Both Barnes-Hut rows are `rejected_or_no_go`:
- `barnes_hut_aggregate_tree_numba_cuda_fused`: "do not promote as V4.0 generic Tier-2; may inform future fixed Numba continuation only if app identity is removed"
- `barnes_hut_optix_cupy_or_optix_numba_frontier`: "none; keep as no-go/negative evidence"

Integrity Locks section: "Barnes-Hut partner routes remain no-go evidence for V4.0 Tier-2 promotion, because the useful wins are not clean RT-core generic-operator wins." The 13.591x figure (slow OptiX frontier path) is explicitly labeled as "no-go metadata only" in the JSON, not a V4 claim.

---

### Check 7 — Does this ledger avoid process churn and provide useful inputs for Goal4648/4649/4650?

**Pass.**

AM5 required compressing the old standalone truth-freeze into a thin ledger section. That is exactly what was executed: a one-page truth ledger as Section 2, then inventory rows, then explicit target lists. No separate "truth freeze" goal was created.

Goal4648 inputs provided:
- Which CuPy surfaces are `strong` vs `needs_rerun` candidates, with denominator and scale already identified
- Which Numba surface is already measured and needs only contract confirmation
- Which routes are definitively `rejected_or_no_go` (saves Goal4652 route-binding work)
- AM1 enforcement points already anchored in the ledger for Goal4648 to reference

---

## Minor Edits Required Before Formal Close

### Minor Edit 1 — `numba_component_union_current_v4_surface` Goal4650 target framing inconsistency

The JSON summary lists this row as an "immediate_goal4650_numba_targets" entry, but the row itself says `promotion_needed: none for current Numba-scoped surface`. The ledger's Goal4650 section says "The only immediate Numba continuation target is: `numba_component_union_current_v4_surface`" with no qualification.

This is contradictory in isolation. A future reader drafting the Goal4650 contract could interpret this as "run a new certification gate on this surface" when the surface is already a certified V4 operator.

**Required edit:** Add one sentence to the Goal4650 target section clarifying what Goal4650 must actually do with this row — either: confirm the existing surface passes the new Goal4648 numeric contract (minor re-verification), or explicitly note that the Numba surface is already bounded V4 and Goal4650's work is limited to potential future CuPy variant promotion. The JSON row note "later work may broaden or add CuPy variant" is the right answer; surface it in the ledger prose.

### Minor Edit 2 — JSON `blocked_from_speed_claims` uses informal string entries

The JSON summary `blocked_from_speed_claims` array contains `"all partner_migration candidates"` and `"all partner_parity candidates"` as free-text strings rather than row IDs. This works for human reading but makes the field ambiguous to a future script or goal that tries to cross-reference which specific rows are blocked.

**Required edit:** Either enumerate row IDs explicitly (matching the `candidate_rows` array IDs), or add a comment field clarifying the intent. This is low-priority but should be fixed before Goal4649/4650 reference this JSON programmatically.

---

## Non-Authorization Confirmation

This review does not authorize:

- Any public V4 release or tag language
- Broad V4 speedup language (app-level or whole-suite)
- CuPy performance claims of any kind
- Arbitrary Numba callback claims
- C ABI or embedding claims
- Partner migration or partner parity as V4 speed evidence
- POD benchmark spending
- Barnes-Hut routes as V4.0 generic Tier-2 evidence

---

## 3-AI Consensus Requirement

This review constitutes **one AI seat** toward the required 3-AI completion consensus. Goal4647 is not formally complete until either two additional AI-seat reviews are recorded, or the owner records explicit review debt per the chain's rules. Goal4648 execution may proceed in parallel with obtaining the remaining reviews.

---

**Verdict: `accept_with_minor_edits`**
