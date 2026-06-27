# External Review Handoff: Goal3087 v2.7 Duplicate-Gate Promotion Workflow

Please perform a read-only review of Goal3087 and write the review to:

`docs/reviews/goal3088_claude_review_goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`

## Context

Goal3087 implements the D-4 item from:

`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`

Earlier v2.7 goals already added primitive discovery metadata, generated the
catalog, added composition recipes, added the advisory planner, and added a
learner-facing discovery workflow. Goal3087 focuses only on promotion
governance: a proposed near-duplicate primitive should fail closed unless the
candidate documents the existing alternatives considered and the reason it is
distinct.

## Files To Inspect

- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_catalog.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/handoff/HANDOFF_TEMPLATE_PRIMITIVE_PROMOTION_REVIEW.md`
- `tests/goal3087_v2_7_duplicate_gate_promotion_workflow_test.py`
- `docs/reports/goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`

## Validation To Run

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal2624_primitive_hierarchy_test
```

## Review Questions

1. Does the candidate-scoped `validate_primitive_hierarchy(...)` extension
   correctly fail closed for near-duplicate promoted candidates without
   `considered_alternatives` and `distinct_from`?
2. Is the candidate scope requirement a good safeguard against accidentally
   reclassifying legacy/current nodes?
3. Does the handoff template make the search-before-create workflow executable
   enough for future primitive-promotion reviews?
4. Does the generated catalog describe the duplicate gate accurately and without
   overclaiming?
5. Does Goal3087 preserve the app-agnostic engine boundary and avoid release,
   performance, zero-copy, broad RT-core, and paper-reproduction claims?

Use one of the accepted verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`. If accepted with a boundary, list required
follow-up fixes separately from optional future work.
