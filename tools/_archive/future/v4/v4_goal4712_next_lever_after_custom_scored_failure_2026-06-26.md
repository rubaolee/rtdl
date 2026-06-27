# V4 Goal4712 Next Lever After Custom-Scored Failure

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `custom_predicate_early_exit_multi_hit_selected_protocol_required`

## Goal

Use the Goal4711 failure result to select the next V4 performance lever without
repeating the same failed cost model.

## Controlling Fact

Goal4711 failed as a formal high-performance proof:

- target: `ray_triangle_custom_scored_accumulation`
- classification: `fail_focused_app_gate_not_high_performance`
- primary geomean V3 speedup: `1.029x`
- minimum primary V3 speedup: `1.014x`

Interpretation:

Post-hit scalar scoring only removes a small amount of callback-placement or
materialization cost. It does not reduce traversal work, candidate count, or
high-volume hit attribute movement enough to support formal high-performance V4.

## Rejected Patterns

- `post_hit_scalar_accumulation_polish`: already measured at about `1.029x`.
- `weighted_sum_or_existing_operator_control`: weighted sum exists in V2/V3 and
  is control-only.
- `global_atomic_scalar_accumulation`: Goal4711 smoke showed it is diagnostic,
  not a performance route.
- `same_target_rerun_without_changed_cost_model`: rerunning cannot move the
  frozen bar.

## Selected Next Target

`custom_predicate_early_exit_multi_hit`

Generic feature:

`constrained custom predicate callback in any-hit with RTDL-owned early-exit policy`

Why this is the right next lever:

Unlike post-hit accumulation, a predicate callback can affect traversal-side
control flow. V4 can reject or terminate inside any-hit before materializing
every candidate. V2/V3 fallback must materialize all hit IDs or hit attributes
and then run a separate device predicate/filter/reduction.

This changes the cost model. It is the first next target after Goal4711 that can
plausibly produce a material V4-specific win rather than another `1.03x`
polish result.

## Contract For Goal4713

Goal4713 must freeze, before any POD timing:

- correctness oracle;
- candidate density, including multi-hit regimes such as `>=8` and `>=32`
  possible hits per ray;
- sparse and no-hit controls;
- callback variants;
- V2/V3 fallback;
- V4 route;
- numeric bars;
- kill conditions;
- public-claim boundaries.

Boundary:

- user callback returns a pure scalar/boolean;
- RTDL owns the action, such as `terminate_on_first_accept` or
  `count_until_threshold`;
- user callback does not mutate external state;
- no app-identity kernel is allowed.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.json`
- Markdown:
  `future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`
- Source:
  `src/rtdsl/v4_goal4712_next_lever_after_custom_scored_failure.py`
- Script:
  `scripts/v4_goal4712_next_lever_after_custom_scored_failure.py`
- Tests:
  `tests/v4_goal4712_next_lever_after_custom_scored_failure_test.py`

## Validation

```text
py scripts/v4_goal4712_next_lever_after_custom_scored_failure.py --json-out future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.json --md-out future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md
py -m py_compile src/rtdsl/v4_goal4712_next_lever_after_custom_scored_failure.py scripts/v4_goal4712_next_lever_after_custom_scored_failure.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4712_next_lever_after_custom_scored_failure_test tests.v4_goal4711_custom_scored_app_result_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `6 tests OK`.

## Non-Authorization

Goal4712 does not authorize:

- POD timing;
- all-app benchmarking;
- V4 release;
- formal high-performance V4 wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

## Goal-Level Decision Audit

1. Was I being stupid?

No in the final Goal4712 decision. I used the Goal4711 negative result to stop
polishing a failed target.

2. If yes, what actions made the decision stupid?

Not applicable for the final decision. The known prior mistake was already
recorded in Goal4711: a smoke runner gave fallback callback-in-hit execution,
and that was fixed before the full run.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Move from post-hit scoring to traversal-affecting predicate early-exit,
where V4 can reduce candidates/materialization rather than only moving where a
small callback is evaluated.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4713 should freeze the protocol for
`custom_predicate_early_exit_multi_hit`.
