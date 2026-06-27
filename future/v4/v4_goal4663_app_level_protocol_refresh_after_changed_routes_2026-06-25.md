# V4 Goal4663 App-Level Protocol Refresh After Changed Routes

Date: 2026-06-25

Status: protocol refreshed; full all-app rerun not triggered

## Purpose

Goal4663 refreshes the app-level protocol after the two changed-route probes:

- Goal4659: Hausdorff official V4 route with coordinate-normalized correctness
  boundary.
- Goal4660/4661: RTNN ranked-summary V4 candidate route with same-hardware
  comparison.

Machine evidence:

```text
future/v4/evidence/v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.json
```

## Result

Decision label:

```text
protocol_refreshed__no_full_all_app_rerun_triggered
```

Reason:

- Hausdorff changed from missing/partial route to an official V4 route, but its
  current public truth is correctness-bound. The 1M row needs
  coordinate-normalized chunking, and that row is not a broad speed win.
- RTNN changed from missing ranked-summary route to a V4 candidate route, but
  its serious same-hardware rows are parity, not a material V4 app-level
  speedup.
- Those facts improve route truth, but they do not create enough formal
  high-performance evidence to justify spending POD time on another full
  all-app V2.14/V3.0.2/V4 rerun now.

## Changed Rows

### Hausdorff XHD

Protocol treatment:

```text
official_route_correctness_boundary_not_formal_speed_win
```

Meaning:

- Record the route as real V4 app-route progress.
- Require coordinate-normalized denominator for 1M exactness.
- Keep it out of formal speed-row claims until a protocol explicitly freezes
  that denominator and cold/hot windows.

### RTNN

Protocol treatment:

```text
candidate_route_present_but_does_not_move_app_level_bar
```

Meaning:

- Record the candidate route as real engineering work.
- Do not count it as a speed win.
- Do not run all-app because this row cannot change the formal release
  decision.

## What This Means For V4

This is not proof that V4 has no value. It is proof that the current app-level
high-performance claim is still not earned.

Current honest V4 value:

- bounded generic operator surface exists;
- some operator rows have measured wins against stated denominators;
- Hausdorff route/correctness improved;
- RTNN route unification did not improve performance.

Current missing piece for formal high-performance V4:

- at least one more serious app-level route must show material runtime-sourced
  improvement under a frozen denominator, or an existing route must be improved
  enough to move the app-level decision.

## Next Engineering Direction

Do not run the full all-app suite on the current evidence. The next useful work
is a real performance engineering goal, such as:

1. Reduce Hausdorff V4 prepare/cold overhead while preserving the 1M
   coordinate-normalized correctness boundary.
2. Replace or improve RTNN ranked-summary execution so serious scales move
   beyond parity.
3. Pick another benchmark app with a clear generic Tier-2 fused route hypothesis
   and a frozen app-level bar before implementation.

## Verification

Broader V4 boundary validation passed:

```text
py -3 -m unittest tests.v4_goal4660_ranked_summary_candidate_test tests.v4_goal4659_hausdorff_official_route_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4653_app_level_protocol_test tests.v4_goal4655_app_benchmark_analysis_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_scope_gate_test tests.v4_catalog_regression_gate_test tests.v4_goal4632_release_decision_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test
```

Result:

```text
73 tests OK
```

## Non-Authorization

This goal does not authorize V4 release, formal high-performance V4 wording,
broad V4 speedup wording, whole-application speedup wording, unrestricted exact
Hausdorff wording, exact same-runner RTNN speedup wording, public true-zero-copy
claims, Tier-3 callback support, raw OptiX callbacks, embedding/C ABI,
non-Python host bindings, or app-specific native kernels.
