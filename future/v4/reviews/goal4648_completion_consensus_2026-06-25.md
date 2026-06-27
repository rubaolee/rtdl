# Goal4648 Completion Consensus

Date: 2026-06-25
Goal:
`future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md#goal4648---v4-partner-promotion-contract-with-numeric-bars`

## Verdict

```text
goal4648_complete__goal4649_may_start
```

Goal4648 is complete. It produced a code-visible partner promotion contract,
froze numeric bars before measurement, added regression tests, fixed the
third-reviewer blocking fail-open bug, and preserved all non-authorization
boundaries.

## Completion Evidence

- Report:
  `future/v4/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.md`
- JSON evidence:
  `future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json`
- Contract code:
  `src/rtdsl/v4_partner_promotion_contract.py`
- V4 front-door export:
  `src/rtdsl/v4.py`
- Tests:
  `tests/v4_goal4648_partner_promotion_contract_test.py`
- Call for review:
  `future/v4/reviews/call_for_review_v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.md`

## Local Verification

JSON:

```text
GOAL4648_JSON_OK_AFTER_POPPER_FIX
```

Tests:

```text
py -m unittest tests.v4_goal4648_partner_promotion_contract_test tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_frontdoor_test
Ran 31 tests in 1.179s
OK
```

The local Python launcher printed a `<prefix>` environment warning, but unittest
exited successfully.

## Review Seats

| Seat | Result | Notes |
|---|---|---|
| Claude initial | `accept_goal4648_complete` | Accepted original Goal4648; non-blocking observations recorded. |
| Antigravity initial | `accept_goal4648_complete` | Accepted original Goal4648. |
| Popper initial | `reject_goal4648_incomplete` | Found real fail-open bug in candidate allowlist for unsupported partners. |
| Claude fix review | `accept_goal4648_complete` | Confirmed fail-open bug fixed and parity-speed-win flag added. |
| Antigravity fix review | `accept_goal4648_complete` | Confirmed fail-open bug fixed, tests cover negative partner cases. |
| Popper fix review | `accept_goal4648_complete` | Confirmed blocker fixed. |

The initial Popper rejection was correct and materially improved the contract.
Goal4648 is closed only after the fix reviews, not on the earlier two-seat
approval.

## Blocking Bug Fixed

Bug:

`v4_partner_promotion_candidate_allowed()` previously scanned all contracts for
unsupported partners. That could return `True` for:

```text
torch + cupy_grouped_reduction_device_columns_262144
torch + numba_component_union_current_v4_surface
unknown + cupy_grouped_reduction_device_columns_262144
```

Fix:

```python
if normalized_partner not in {"cupy", "numba"}:
    return False
```

Regression tests were added for those negative cases.

## Frozen Bars

| Gate | Frozen value |
|---|---:|
| Correctness parity | `1.0` |
| Representative speedup floor | `>= 1.20x` |
| Partner parity floor | `>= 0.98x` |
| Host materialization in hot path | `false` |

Both of these are code-visible and tested:

- `partner_migration_counts_as_v4_speed_win = false`
- `partner_parity_counts_as_v4_speed_win = false`

## Non-Authorization Preserved

Goal4648 does not authorize:

- public V4 release/tag wording;
- broad V4 speedup claims;
- whole-app / all-benchmark V4 speedup claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- partner migration or partner parity as V4 speed evidence.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

Initially yes in a narrow engineering sense: I wrote an allowlist helper that
was fail-open for unsupported partner names. The third review caught it.

2. If yes, what actions made it foolish?

The function filtered special cases for `cupy` and `numba` but did not return
`False` for all other partners before scanning contracts. That contradicted the
fail-closed design.

3. Was there another possibility that avoided being trapped in one idea?

Yes: write negative tests for known candidate IDs under unsupported partners at
the same time as the positive allowlist tests. Those tests now exist.

4. Can I start a different path that actually solves the problem?

Yes. Goal4649 may now start against a fail-closed contract. The next work is
CuPy certification only for allowlisted candidates, under frozen bars, without
POD spending until separately authorized.

## Next Authorized Work

Goal4649 may start:

```text
CuPy Front-Door Certification Gate
```

Starting Goal4649 does not authorize POD benchmark spending or CuPy performance
claims. It authorizes only implementation/protocol work that prepares exact
CuPy V4 certification runs under the Goal4648 contract.
