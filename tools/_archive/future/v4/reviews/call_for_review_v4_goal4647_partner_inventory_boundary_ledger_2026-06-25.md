# Call For Review: V4 Goal4647 Partner Inventory Boundary Ledger

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4647_complete`
- `accept_with_minor_edits`
- `reject_goal4647_incomplete`
- `blocked_missing_context`

## Context

Goal4647 is the first goal in the revised V4 Goals4647-4658 chain. Its job is
not to benchmark or authorize release. Its job is to inventory V2.14/V3 CuPy
and Numba partner assets and draw the boundary between historical partner
success and V4-certified support.

Claude previously required AM1:

```text
Partner migration / partner parity rows cannot support "V4 is faster than
V2.14." Moving an old V2.14 CuPy or Numba win behind a V4 front door improves
the product surface but is not itself a new V4 speed win.
```

## Files To Review

- Goal chain:
  `future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md`
- Goal4647 ledger:
  `future/v4/v4_goal4647_v2_14_partner_inventory_boundary_ledger_2026-06-25.md`
- Goal4647 JSON inventory:
  `future/v4/evidence/v4_goal4647_partner_inventory_2026-06-25.json`
- Amendment/recheck file:
  `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`

## Questions

1. Is Goal4647 complete enough to start Goal4648?
2. Does the ledger preserve AM1: partner migration is not a V4 speed win?
3. Are the candidate classifications reasonable?
4. Are CuPy claims still blocked until Goal4649 V4 rerun/certification?
5. Are Numba claims limited to fixed continuations, with arbitrary callbacks
   still Tier-3 spike-only?
6. Are Barnes-Hut partner routes correctly kept as no-go/negative evidence for
   V4.0 generic Tier-2 release wording?
7. Does this ledger avoid process churn and provide useful inputs for
   Goal4648/4649/4650?

## Non-Authorization

This review must not authorize:

- public V4 release/tag language;
- broad V4 speedup language;
- app-level V4-vs-V2.14/V3 claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- treating partner migration or partner parity as V4 speed evidence.
