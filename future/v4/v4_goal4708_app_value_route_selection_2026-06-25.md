# V4 Goal4708 App-Level Value Route Selection

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Determine whether the specialized Tier-3 weighted-sum support candidate can be
counted as app-level high-performance V4 evidence.

## Result

Validation status: `passed`

Decision:

`do_not_count_specialized_tier3_candidate_as_app_level_high_performance_evidence`

Reason:

Goals4696-4707 make the constrained callback route a real support candidate,
but they do not bind it to a promoted benchmark app. The currently proven route
is an operator surface:

`v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

It cannot be counted as a formal V4 app-level speed win unless a real benchmark
app is explicitly routed through it and passes a frozen app-level protocol.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4708_app_value_route_selection_2026-06-25.json`
- Markdown:
  `future/v4/evidence/v4_goal4708_app_value_route_selection_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4708_app_value_route_selection.py`
- Script:
  `scripts/v4_goal4708_app_value_route_selection.py`
- Tests:
  `tests/v4_goal4708_app_value_route_selection_test.py`

## Route Rows

| target | classification | app-level claim |
|---|---|---|
| `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | operator-surface candidate value | false |
| `rt_dbscan` | not bound to specialized Tier-3 candidate | false |
| `raydb_style` | not bound to specialized Tier-3 candidate | false |
| `triangle_counting` | not bound to specialized Tier-3 candidate | false |
| `librts_spatial_index` | not bound to specialized Tier-3 candidate | false |
| `hausdorff_xhd_or_rtnn` | not bound to specialized Tier-3 candidate | false |

## Validation

Commands run:

```text
py scripts/v4_goal4708_app_value_route_selection.py --json-out future/v4/evidence/v4_goal4708_app_value_route_selection_2026-06-25.json --md-out future/v4/evidence/v4_goal4708_app_value_route_selection_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4708_app_value_route_selection.py scripts/v4_goal4708_app_value_route_selection.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4708_app_value_route_selection_test tests.v4_goal4706_negative_validation_docs_gate_test tests.v4_goal4705_source_ptx_cache_stability_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `8 tests OK`.

## Claim Boundary

Goal4708 does not authorize:

- app-level speed claims;
- broad V4 performance claims;
- public Tier-3 support;
- arbitrary callbacks;
- raw OptiX callbacks;
- V4 release wording.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal prevents a subtle overclaim: a real operator/support-candidate
result is not automatically a benchmark-app result.

2. If yes, what actions made the decision stupid?

Not applicable. The dangerous action would have been counting the weighted-sum
operator route as a formal V4 app-level win without a real app binding.

3. Is there another path that avoids being stupid on one idea?

Yes. Keep Tier-3 support hardening separate from formal high-performance app
selection.

4. Can I start a different path that actually solves the problem?

Yes. Goal4709 should select a real formal high-performance V4 app-level target
outside this Tier-3 candidate.

## Next

Proceed to Goal4709: formal high-performance V4 app-level target selection
outside the Tier-3 candidate.
