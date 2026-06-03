# Handoff: External Review Of Goal3081 v2.7 Advisory Planner

Please review Goal3081 and write:

`docs/reviews/goal3082_<reviewer>_review_goal3081_v2_7_advisory_planner_2026-06-03.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

## Files To Inspect

- `src/rtdsl/primitive_planner.py`
- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3081_v2_7_explain_only_advisory_planner_2026-06-03.md`
- `docs/reviews/goal3079_claude_review_goal3077_v2_7_composition_recipes_2026-06-03.md`
- `tests/goal3081_v2_7_advisory_planner_test.py`
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`

## Review Questions

1. Does `plan_continuation(...)` remain explain-only, with no execution,
   dispatch, hidden routing, selected partner, or automatic partner selection?
2. Does the planner correctly expose each primitive step's status, especially
   `candidate_behavior` and `internal_generic_path`, rather than promoting an
   advisory recipe into stable primitive status?
3. Are partner options derived conservatively from the v2.5 support matrix,
   including fail-closed unsupported requested partner cells?
4. Is the generated catalog updated without overclaiming release readiness,
   public speedups, RT-core speedups, true zero-copy, paper reproduction,
   package install, or automatic Triton selection?
5. Are the tests sufficient for this first v2.7 planner slice?
6. Is it acceptable to proceed next to small learner examples/docs showing
   `find_primitive(...)`, `find_recipe(...)`, and `plan_continuation(...)` as
   the v2.7 primitive discovery workflow?

## Boundary

This review must not authorize a release, a public performance claim, broad
RT-core wording, true zero-copy wording, package-install wording, automatic
partner selection, or app-specific native engine logic.
