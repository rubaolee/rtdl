# Call For Review: V4 Goal4648 Partner Promotion Contract With Numeric Bars

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4648_complete`
- `accept_with_minor_edits`
- `reject_goal4648_incomplete`
- `blocked_missing_context`

## Context

Goal4648 freezes the pre-run contract and numeric bars for future CuPy and
fixed Numba partner certification. It does not certify those partners and does
not authorize performance claims. The goal exists to prevent Goal4649/4650 from
running first and inventing bars after seeing results.

## Files To Review

- Goal4648 report:
  `future/v4/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.md`
- Goal4648 JSON:
  `future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json`
- Contract code:
  `src/rtdsl/v4_partner_promotion_contract.py`
- V4 front-door export:
  `src/rtdsl/v4.py`
- Tests:
  `tests/v4_goal4648_partner_promotion_contract_test.py`
- Previous completion record:
  `future/v4/reviews/goal4647_completion_consensus_and_review_debt_2026-06-25.md`

## Local Verification

```text
Get-Content -Raw future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json | ConvertFrom-Json | Out-Null
GOAL4648_JSON_OK

py -m unittest tests.v4_goal4648_partner_promotion_contract_test tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_frontdoor_test
Ran 31 tests in 1.234s
OK
```

The local Python launcher printed a `<prefix>` environment warning, but unittest
exited successfully.

## Questions

1. Is Goal4648 complete enough to start Goal4649?
2. Are the CuPy device-array front-door contract and telemetry requirements
   concrete enough?
3. Are the fixed Numba continuation boundaries concrete enough, with arbitrary
   callbacks still blocked?
4. Are numeric bars frozen before measurement?
5. Does the code/test surface prevent partner migration or parity from becoming
   a fake V4 speed claim?
6. Does current planner/catalog behavior still fail closed for unmeasured CuPy?
7. Are there any blocking issues before Goal4649 CuPy certification work starts?

## Non-Authorization

This review must not authorize:

- public V4 release/tag wording;
- broad V4 speedup language;
- app-level V4-vs-V2.14/V3 claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- treating partner migration or partner parity as V4 speed evidence.
