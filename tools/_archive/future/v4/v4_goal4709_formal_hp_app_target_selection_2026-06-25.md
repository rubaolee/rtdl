# V4 Goal4709 Formal High-Performance App Target Selection

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Select a real app-level target for formal high-performance V4 work outside the
specialized Tier-3 operator/support-candidate claim. This prevents counting an
operator-only result as a benchmark app win.

## Result

Selected app target:

`ray_triangle_custom_scored_accumulation`

POD authorized: `false`

Next goal:

`Goal4710 ray-triangle custom scored accumulation app-level protocol freeze`

## Why This Target

The selected app family requires user-defined scalar scoring/reduction inside
the RT hit path. V2/V3 baselines must materialize hits or use fixed built-in
reductions; V4 can test the new constrained Numba C-ABI scalar callback fused
inside an RTDL-generated OptiX hit program.

This is a generic runtime/language feature test:

`specialized Tier-3 scalar callback fusion for ray/triangle hit reduction`

It is not an app-specific native kernel.

## Rejected Existing Targets

| target | reason |
|---|---|
| `rt_dbscan` | Goal4670/4671 found modest/no-go second-win evidence; component union is not solved by scalar callback fusion. |
| `raydb_style` | Goal4655 app row is parity; no clean new V4 runtime lever identified. |
| `triangle_counting` | Large V2.14 ratio is historical route evolution; V4-over-V3 increment is modest and not a clean new V4 feature proof. |
| `librts_spatial_index` | Goal4655 app row is parity; no current V4 lever moves it. |
| `hausdorff_xhd` | Current blocker is correctness/normalization, not proven V4 performance. |
| `rtnn` | Ranked-summary/top-k candidate was deferred for serious-scale parity or below-parity rows. |

## Protocol Requirements For Goal4710

Goal4710 must freeze, before POD:

- V2.14 strongest materialized-hit or built-in fixed-reduction route;
- V3.0.2 strongest current route;
- V4 Tier-2 built-in route where semantically comparable;
- dense and sparse hit regimes;
- at least `262144` rays, with larger rows if POD budget allows;
- callback variants: weighted sum, affine score, threshold score, minmax score;
- correctness parity;
- numeric bars and kill conditions.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4709_formal_hp_app_target_selection_2026-06-25.json`
- Markdown:
  `future/v4/evidence/v4_goal4709_formal_hp_app_target_selection_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4709_formal_hp_app_target_selection.py`
- Script:
  `scripts/v4_goal4709_formal_hp_app_target_selection.py`
- Tests:
  `tests/v4_goal4709_formal_hp_app_target_selection_test.py`

## Validation

Commands run:

```text
py scripts/v4_goal4709_formal_hp_app_target_selection.py --json-out future/v4/evidence/v4_goal4709_formal_hp_app_target_selection_2026-06-25.json --md-out future/v4/evidence/v4_goal4709_formal_hp_app_target_selection_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4709_formal_hp_app_target_selection.py scripts/v4_goal4709_formal_hp_app_target_selection.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4709_formal_hp_app_target_selection_test tests.v4_goal4708_app_value_route_selection_test tests.v4_goal4706_negative_validation_docs_gate_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `7 tests OK`.

## Claim Boundary

Goal4709 authorizes only Goal4710 protocol freeze. It does not authorize:

- POD spend;
- app-level speed claims;
- public Tier-3 support;
- raw OptiX callbacks;
- arbitrary callbacks;
- V4 release wording;
- formal high-performance V4 wording.

## Goal-Level Decision Audit

1. Was I being stupid?

No. The goal avoids pretending existing weak/parity app rows are solved and
selects a target whose hypothesis is tied to a real V4-specific runtime feature.

2. If yes, what actions made the decision stupid?

Not applicable. The dangerous action would have been rerunning all-app or
claiming the operator support candidate as an app-level win without a frozen app
protocol.

3. Is there another path that avoids being stupid on one idea?

Yes. Goal4710 must freeze baselines and bars before POD, and it must kill the
target if it becomes partner migration or an operator-only claim.

4. Can I start a different path that actually solves the problem?

Yes. The concrete path is Goal4710 protocol freeze, then a focused POD run only
if the protocol demonstrates a non-trivial V4-specific hypothesis.

## Next

Proceed to Goal4710: ray-triangle custom scored accumulation app-level protocol
freeze.
