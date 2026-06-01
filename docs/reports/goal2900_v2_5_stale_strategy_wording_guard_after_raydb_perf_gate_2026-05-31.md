# Goal2900: v2.5 Stale Strategy Wording Guard After RayDB Perf Gate

Date: 2026-05-31
Status: accepted as wording/claim-boundary cleanup

## Purpose

Goal2896 changed the RayDB evidence picture. The old v2.5 strategy language could still be read as "Tier A demonstrates Triton as the chosen partner at parity." That is now wrong for RayDB scalar grouped reductions: the current pod-backed decision is primitive-first when the fused generic RTDL primitive exactly matches the continuation.

Goal2900 patches the stale design report and adds a regression guard so the old wording does not leak into future readiness or release discussion.

## What Changed

Updated:

- `docs/reports/v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md`
- `tests/goal2900_v2_5_stale_strategy_wording_guard_test.py`

The design report now has a post-Goal2896 correction:

- partner choice still belongs to the app;
- no partner is forced;
- multi-partner composition remains first-class;
- RayDB scalar grouped reductions are primitive-first after Goal2896;
- typed hit-stream plus partner continuation is reserved for unfused continuations.

## Boundary

This is not a release authorization and not a public performance claim.

It does not rewrite older historical reports wholesale. It adds an explicit correction to one live strategic design note whose wording would otherwise conflict with the current Goal2896 evidence.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2900_v2_5_stale_strategy_wording_guard_test

Ran 3 tests in 0.002s
OK
```

Focused v2.5 planner/readiness validation also passed:

```text
Ran 23 tests in 0.389s
OK
```
