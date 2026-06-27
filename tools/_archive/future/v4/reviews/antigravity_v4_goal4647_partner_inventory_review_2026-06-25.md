# Formal Review: V4 Goal4647 Partner Inventory Boundary Ledger

**Date:** 2026-06-25
**Reviewer:** Antigravity (Gemini 3.5 Flash), second AI seat
**Verdict:** `accept_goal4647_complete`

---

## Verdict Rationale

Goal4647 is complete and ready to close, unblocking the execution of Goal4648. Both required exit evidence artifacts are present, consistent, and satisfy all integrity constraints:
- `v4_goal4647_v2_14_partner_inventory_boundary_ledger_2026-06-25.md`
- `evidence/v4_goal4647_partner_inventory_2026-06-25.json`

The minor edits from Claude's previous review have been fully addressed:
1. **Goal4650 target framing consistency (Minor Edit 1):** The prose in the boundary ledger file under the `Goal4650 Numba Target` section has been updated to explicitly clarify that `numba_component_union_current_v4_surface` is already a certified V4 operator and that Goal4650's focus with respect to this surface is on contract verification, while potential future CuPy variant promotions are tracked separately.
2. **JSON blocked_from_speed_claims formatting (Minor Edit 2):** The JSON schema summary has been updated to explicitly enumerate all 12 candidate row IDs in the `blocked_from_speed_claims` array instead of using informal free-text descriptors.

---

## Mandatory Check Results

### Check 1 — Is Goal4647 complete enough to start Goal4648?

**Pass.**
The ledger provides a solid inventory of CuPy/Numba partner assets. Strong promotion candidates are clearly identified (`cupy_grouped_reduction_device_columns_262144` and `cupy_grouped_reduction_device_columns_524288`), as well as targets needing reruns and no-go rows. This enables Goal4648 to immediately formulate contracts and numeric bars for promotion.

### Check 2 — Does the ledger preserve AM1: partner migration is not a V4 speed win?

**Pass, fully locked.**
The ledger explicitly establishes that partner migration and partner parity do not contribute to `formal_high_performance_v4_supported`. The striking historical ratios (such as 100.019x vs Embree) are correctly bounded and labeled as historical partner results, not new V4 speedup wins. They remain blocked from public performance claims until a certified V4 run is performed under the Goal4648 contract.

### Check 3 — Are the candidate classifications reasonable?

**Pass.**
The classification of the 12 candidate rows is appropriate:
- 2 `promotion_candidate_strong` rows have rigorous historical evidence.
- 5 `promotion_candidate_needs_rerun` rows are correctly flagged as requiring frozen V4 contracts, denominators, or front-door runs.
- 3 `historical_only` rows capture necessary context without introducing overclaims.
- 2 `rejected_or_no_go` rows (Barnes-Hut routes) are excluded from V4.0 Tier-2 promotion.

### Check 4 — Are CuPy claims still blocked until Goal4649 V4 rerun/certification?

**Pass.**
All CuPy candidate rows are labeled with `public_claim_status: blocked_until_v4_cupy_rerun` or `blocked`. The ledger and JSON both record that CuPy claims are explicitly blocked until Goal4649 certifies these surfaces.

### Check 5 — Are Numba claims limited to fixed continuations, with arbitrary callbacks still Tier-3 spike-only?

**Pass.**
Numba support remains restricted to fixed certified continuations. Arbitrary user callbacks are marked as unsupported and blocked. The failed OptiX module link attempt for Numba PTX generation is correctly documented as negative/failed evidence rather than supporting evidence.

### Check 6 — Are Barnes-Hut partner routes correctly kept as no-go/negative evidence for V4.0 generic Tier-2 release wording?

**Pass.**
Both Barnes-Hut candidate rows are correctly categorized as `rejected_or_no_go`. The OptiX+partner frontier routes are preserved as negative evidence (being slower than Numba CUDA fused), and the Numba CUDA fused route is marked as an app-specific kernel without RT-core V4 leverage, making it unsuitable for V4.0 generic Tier-2.

### Check 7 — Does this ledger avoid process churn and provide useful inputs for Goal4648/4649/4650?

**Pass.**
The ledger conforms to AM5 by compressing the truth freeze into a single, highly actionable inventory document. Redundant process loops have been avoided while providing clean inputs for contract and certification definition in the next goals.

---

## Non-Authorization Confirmation

This review does not authorize:
- Any public V4 release, pre-release, or tag wording
- Broad app-level or whole-suite V4 speedup claims
- CuPy performance claims of any kind
- Arbitrary Numba callback claims
- C ABI or embedding claims
- POD benchmark spending
- Treating partner migration or parity as V4 speed evidence
- Barnes-Hut routes as V4.0 generic Tier-2 evidence

---

## Consensus State

With this review, the Antigravity seat registers a verdict of `accept_goal4647_complete`. This provides the second required approval towards the 3-AI consensus, resolving the previous review debt. Goal4648 execution may proceed.
