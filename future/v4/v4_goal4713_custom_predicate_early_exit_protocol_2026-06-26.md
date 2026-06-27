# V4 Goal4713 Custom Predicate Early-Exit Protocol

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `protocol_frozen_not_run`

## Goal

Freeze the protocol for the next V4 high-performance attempt:

`ray_triangle_custom_predicate_early_exit_multi_hit`

This protocol follows Goal4711's failure and Goal4712's next-lever selection.
It tests a different cost model: callback logic affects traversal-side
filtering and early termination, rather than only moving post-hit scalar scoring
into the hit program.

## Primary Regimes

| regime | candidates/ray | accept layer | purpose |
|---|---:|---:|---|
| `dense_early_accept_k8` | 8 | 0 | V4 can terminate before materializing 8 candidates per ray |
| `dense_early_accept_k32` | 32 | 0 | V4 can terminate before materializing 32 candidates per ray |
| `sparse_early_accept_k32` | 32 | 0 | sparse active-ray control with real early-exit opportunity |

## Control Regimes

| regime | candidates/ray | purpose |
|---|---:|---|
| `dense_late_accept_k32` | 32 | little early-exit opportunity; cannot support primary speed claim |
| `dense_reject_all_k32` | 32 | verifies false-positive behavior and worst-case predicate cost |
| `no_hit_empty` | 0 | validates no-hit accounting |

## Callback Variants

- `accept_layer_zero`
- `accept_layer_threshold`

Both are pure boolean Numba C-ABI device callbacks. The user callback does not
mutate external state. RTDL owns the action policy such as
`terminate_on_first_accept`.

## Frozen Baselines

- V2.14: materialize all candidate hit IDs/attributes on device, then run a
  separate device predicate/filter/reduction.
- V3.0.2: same fallback shape unless denominator discovery finds a stronger
  custom predicate route.
- V4: generated OptiX any-hit route evaluates the predicate callback and applies
  RTDL-owned early termination/filtering.

## Frozen Bars

- correctness must pass for every callback x regime x scale x implementation
  row.
- primary early-accept regimes geomean V4 over V3.0.2 must be `>=1.50x`.
- primary early-accept regimes geomean V4 over V2.14 must be `>=1.50x`.
- every primary early-accept row must be `>=1.20x` over V3.0.2.
- control regimes must preserve correctness and must not regress below `0.95x`
  geomean over V3.0.2.
- late-accept, reject-all, no-hit, weighted-sum, and post-hit accumulation rows
  cannot support the primary claim.

## Kill Conditions

- any correctness failure kills the goal.
- missing V2/V3 denominator discovery invalidates the run.
- if V4 cannot prove early termination occurred in primary regimes, the run is
  invalid.
- if primary early-accept geomean over V3.0.2 is `<1.50x`, do not continue
  toward formal high-performance wording.
- if any primary early-accept row is below `1.00x` over V3.0.2, stop and
  diagnose before more POD spend.
- if control-regime correctness fails, do not promote the route even if primary
  speed rows pass.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.json`
- Markdown:
  `future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md`
- Source:
  `src/rtdsl/v4_goal4713_custom_predicate_early_exit_protocol.py`
- Script:
  `scripts/v4_goal4713_custom_predicate_early_exit_protocol.py`
- Tests:
  `tests/v4_goal4713_custom_predicate_early_exit_protocol_test.py`

## Validation

```text
py scripts/v4_goal4713_custom_predicate_early_exit_protocol.py --json-out future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.json --md-out future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md
py -m py_compile src/rtdsl/v4_goal4713_custom_predicate_early_exit_protocol.py scripts/v4_goal4713_custom_predicate_early_exit_protocol.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4713_custom_predicate_early_exit_protocol_test tests.v4_goal4712_next_lever_after_custom_scored_failure_test tests.v4_goal4711_custom_scored_app_result_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `8 tests OK`.

## Non-Authorization

Goal4713 does not authorize:

- POD timing;
- all-app benchmarking;
- V4 release;
- formal high-performance V4 wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal freezes a protocol before POD and directly addresses Goal4711's
failure mode.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. The protocol avoids the bad premise that moving post-hit scalar scoring is
enough. It requires the callback to affect candidate materialization or
traversal-side early exit.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4714 should implement the local runner and POD smoke gate for this
frozen protocol.
