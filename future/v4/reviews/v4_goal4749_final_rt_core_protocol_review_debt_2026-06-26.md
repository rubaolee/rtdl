# Review Debt: V4 Goal4749 Final Same-Semantics RT-Core Protocol

Date: 2026-06-26

Status: `review_debt_recorded_engineering_may_continue`

## Goal Under Review

Goal4749 froze the final V4.0 10 benchmark-app same-semantics NVIDIA RT-core
protocol for the V2.14/V3.0.2/V4.0 POD matrix.

Artifacts:

- `future/v4/evidence/v4_goal4749_final_rt_core_protocol_2026-06-26.json`
- `future/v4/v4_goal4749_final_rt_core_protocol_2026-06-26.md`
- `src/rtdsl/v4_goal4749_final_rt_core_protocol.py`
- `scripts/v4_goal4749_final_rt_core_protocol.py`
- `tests/v4_goal4749_final_rt_core_protocol_test.py`

## Internal Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v4_goal4749_final_rt_core_protocol_test
```

Result:

```text
Ran 8 tests in 0.034s
OK
```

## What The Review Must Check

1. Does the protocol correctly enforce V2.14/V3.0.2/V4.0 same-semantics
   NVIDIA RT-core comparison?
2. Does it correctly forbid Embree as a primary denominator while allowing
   Embree only as a control/reference?
3. Does it correctly avoid `n/a` and instead record explicit V4.0 repair
   blockers?
4. Does it correctly treat V4.0 as a V2.14/V3 superset release line?
5. Is the Hausdorff primary fair row correctly changed to threshold-decision
   semantics, with exact nearest-witness kept supplemental until a same-semantics
   V2.14 exact route exists?
6. Are Robot, Contact, and Spatial correctly marked as V4.0 compatibility repair
   rows rather than hidden missing routes?
7. Does this goal avoid authorizing release, POD timing claims, broad speedup
   claims, or V4.1 Numba ray-action scope?

## Non-Authorization

This review-debt record does not authorize:

- final V4.0 release;
- public V4/V2.14 speed claims;
- all-benchmark or whole-app speedup claims;
- Embree primary denominators;
- skipping Goal4750/4751/4753;
- arbitrary Numba ray-action callback support;
- V4.1 scope being counted as V4.0 completion.

## Debt Handling

Per the standing user rule, this goal requires 3-AI completion consensus or
explicit debt. This file records the debt so engineering can continue to
Goal4750 without waiting on reviewer availability.

