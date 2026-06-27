# V4 Goal4731 Post-Matrix Release Decision

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `do_not_tag_bounded_v4_under_high_performance_mandate_continue_generic_runtime_engineering`

## Decision

Do not tag V4 as a formal high-performance release now.

The complete 10-app matrix blocks that claim. A bounded-operator V4 release
could be honest if framed narrowly, but it does not satisfy the user's mandate:
formal high-performance V4 as a serious Python eDSL/runtime.

Therefore the selected path is:

```text
continue_high_performance_engineering
```

## Next Technical Goals

1. Goal4732: `raydb_style` regression root-cause and generic grouped-route
   repair.
2. Goal4733: `triangle_counting` V4/V3 regression recovery.
3. Goal4734: `rt_dbscan` generic continuation improvement attempt.
4. Goal4735: only then choose a fresh generic operator for `spatial_rayjoin` or
   `barnes_hut`, if the gate is still blocked.

## Why This Order

- Known regressions must be fixed before any release.
- `triangle_counting` has a strong V2.14 ratio but fails against V3.0.2; that is
  a clean engineering target.
- `rt_dbscan` already has a full app route and modest gain, so a generic
  continuation improvement could create an independent app win.
- Fresh no-route work is higher risk and must not distract from measured
  blockers.

## Non-Goals

- no docs-only milestone as progress;
- no all-app rerun before a named blocker moves;
- no geomean headline;
- no app-specific native kernels;
- no hidden V2/V3 fallback;
- no public tag without external release authorization.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4731_post_matrix_release_decision_test tests.v4_goal4730_complete_10_app_matrix_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The avoided stupid action would be tagging bounded V4 under a
   high-performance mandate.

2. If yes, what action made the decision stupid?
   Not applicable. The risky action would have been another process/docs loop
   instead of attacking measured blockers.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Use the complete matrix to choose measured blocker repair goals in
   order: regression, regression-vs-V3, modest-below-bar, then fresh generic
   route.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4732 starts with `raydb_style` regression repair.

## Non-Authorization

Goal4731 authorizes no POD spend, no final V4 tag, no public speed claim, no
whole-app high-performance claim, no all-benchmark speedup claim, no app-specific
native kernel, no arbitrary callback support, and no hidden V2/V3 fallback.
