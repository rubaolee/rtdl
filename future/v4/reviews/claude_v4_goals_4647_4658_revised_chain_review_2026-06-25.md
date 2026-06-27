---

# External Critical Review — V4 Goals 4647-4658 Revised Chain

**Date:** 2026-06-25
**Reviewer:** Claude (external seat)
**Target:** `future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md`
**Amendment source:** `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`
**Prior review:** `docs/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`

---

## Verdict

```
verdict: approve_execute_goal4647
release_authorized: false
pod_spend_authorized: false
rewrite_required: false
```

---

## Severity-Ranked Findings

### PASS — No blocking findings

### INFO-1 (informational, non-blocking): AM5 text vs. table inconsistency in the amendment document itself

AM5's body text says "Merge the original Goal4647 into revised **Goal4648** as a boundary ledger." The revised goal chain table in the same amendment document says "**Goal4647** | V2.14 CuPy/Numba partner inventory with a one-page V4 truth/boundary ledger." The revised proposal follows the table, not the text. This is correct: the table is the structural authority; the important intent (no standalone process-only freeze goal) is achieved. No action required.

### INFO-2 (informational, non-blocking): V3 column in Goal4655 analysis is mostly noise

The prior Claude review noted V3 ≈ V2.14 (parity, proven), so V4/V3 and V4/V2.14 ratios will be near-identical. The revised chain includes the V3 column and carries forward the "no treating small V4-vs-V3 differences as meaningful" caution in Goal4655's forbidden list ("No treating tiny V4/V3 noise as meaningful"). Correctly handled; no action required.

### INFO-3 (informational, non-blocking): Evidence file naming inconsistency

Goal4647 exit evidence lists two artifacts: a `.md` file named with `_v2_14_partner_inventory_boundary_ledger_` and a `.json` named with `_partner_inventory_` (shorter form). Both resolve to the same goal; the naming drift is cosmetic. Recommend aligning at authoring time, not a pre-execution blocker.

---

## Answers to the Seven Review Questions

**Q1. Are Claude AM1-AM6 fully applied in the revised chain?**

Yes, all six are applied. Verification:

| Amendment | Where applied in revised chain |
|-----------|-------------------------------|
| AM1 — partner migration is not a V4 speed win | Binding Integrity Locks header (explicit lock on `partner_migration` and `partner_parity` rows); Goal4647 Forbidden; Goals 4649/4650 Forbidden; Goal4655 tasks (explicit AM1 enforcement block); Goal4658 final recheck |
| AM2 — class-aware bars, not naive whole-suite geomean | Binding Integrity Locks header (four bar classes defined); Goal4653 bars section (fused-operator speedup / backend-bound parity / partner-parity / no-route-blocker); Goal4653 Forbidden: "No naive whole-suite geomean as the release trigger" |
| AM3 — route binding must precede protocol freeze | Goal4652 (route binding) now precedes Goal4653 (protocol freeze); Goal4653 explicitly takes "Goal4652's route-binding matrix as input"; Binding Integrity Locks: "Route binding / blocker declaration must happen before app-level protocol freeze" |
| AM4 — quantify "material speedup" before running | Goal4648 defines numeric bars: default `>= 1.20x` floor for CuPy and fixed Numba certification (per-surface, frozen before run); `>= 0.98x` for parity rows; Goal4648 Forbidden: "No `material speedup` without a number"; Binding Integrity Locks: "`Material speedup` must be numeric and frozen before measurement" |
| AM5 — compress standalone truth-freeze into inventory | Old Goal4647 (truth freeze) and old Goal4648 (inventory) merged into single revised Goal4647 (inventory + boundary ledger); the merged goal is one ledger section + JSON rows, consistent with the amendment's own goal chain table |
| AM6 — state expected outcome up front | "Expected Outcome Stated Up Front" section leads the document; text reads `bounded_operator_v4_only + partner unification`; explicitly states "That is not failure"; Goal4656 repeats this: "do not treat it as failure" |

**Q2. Is the sequence dependency-correct now, especially route binding before the app-level protocol freeze?**

Yes. The revised sequence is: Inventory (4647) → Contract + bars (4648) → CuPy cert (4649) → Fixed Numba cert (4650) → Catalog promotion (4651) → **Route binding / blocker declaration (4652)** → **Protocol freeze (4653)** → POD benchmark (4654) → Analysis (4655) → Docs (4656) → Final 3-AI auth (4657) → Final recheck + guardrails (4658). Every gate's input is the output of the prior gate. Goal4653 cannot proceed without the route-binding matrix from Goal4652, and that dependency is stated explicitly.

**Q3. Does the revised chain prevent partner migration / partner parity from supporting "V4 faster than V2.14" claims?**

Yes, with redundant enforcement at five independent points: (1) Binding Integrity Locks header; (2) Goal4647 Forbidden; (3) Goals 4649 and 4650 Forbidden; (4) Goal4655 explicit AM1 enforcement task; (5) Goal4658 final recheck question. Any single enforcement layer failing would be caught by the others.

**Q4. Are numeric bars concrete enough before measurement?**

Yes. Goal4648 defines: CuPy certification floor `>= 1.20x` per surface (or a stricter surface-specific floor justified before the run); fixed Numba certification floor `>= 1.20x` per surface (same qualifier); partner-parity rows `>= 0.98x` against same-contract denominator. All floors are written before any POD spend. The word "material" without a number is explicitly forbidden. App-level bars are class-aware and frozen in Goal4653 after route binding is known. No numeric ambiguity remains.

**Q5. Does the chain preserve V2.14 historical partner success while requiring V4 re-certification before V4 support claims?**

Yes. Goal4647 inventories V2.14/V3 assets and classifies them (`promotion_candidate_strong`, `needs_rerun`, `historical_only`, `rejected_or_no_go`). Goals 4649 and 4650 both carry the Forbidden: "No reuse of V2.14 ratios without V4 rerun." A `promotion_candidate_strong` row from the inventory cannot become a V4 claim until it passes the V4 certification gate under the Goal4648 contract. Historical success is honored; V4 claims require re-run.

**Q6. Does it avoid app-identity kernels, arbitrary callback claims, and broad speedup wording?**

Yes, all three categories are blocked:
- **App-identity kernels**: Goal4649 tasks: "Select surfaces from Goal4647 that are generic, not app-identity kernels"; Goal4651 Forbidden: "No broad app-level claim"; Goal4658 search guard.
- **Arbitrary Numba callback claims**: Goal4650 Forbidden: "No arbitrary Numba callback support claim"; Goal4651 Forbidden: "No app-specific Numba route promotion unless made generic"; Goal4658 search guard.
- **Broad speedup wording**: Binding Integrity Locks (partner migration/parity cannot trigger `formal_high_performance_v4_supported`); Goal4655 Forbidden: "No broad claim if only partner migration/parity moved"; Goal4658 search guard for broad V4 speed claims and CuPy claims.

**Q7. Can execution begin with Goal4647, or is another rewrite required?**

Execution can begin with Goal4647. All six required amendments are in place. No structural flaw remains. The one-page boundary ledger approach avoids the process-churn risk. The first concrete deliverable — the partner inventory JSON and ledger — is well-scoped, non-benchmarking, and does not expand any claim. No rewrite is required.

---

## Required Edits

None. No pre-execution edits are required. The three findings above are informational.

---

## Non-Authorization Block

This review does not authorize:

- POD spend (authorized only after Goal4653 external review)
- Public performance claims of any kind
- Broad V4 release wording
- CuPy performance claims (authorized only after Goal4649 passes under numeric bars)
- Arbitrary Numba callback claims (blocked at every layer; remains blocked)
- C ABI / embedding claims
- App-level V4 speedup claims
- Release tagging

This review authorizes only: commencement of Goal4647 (V2.14 partner inventory with V4 boundary ledger) under the revised chain as written.
