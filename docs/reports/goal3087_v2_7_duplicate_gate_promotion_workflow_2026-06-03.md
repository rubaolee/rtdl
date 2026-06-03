# Goal3087: v2.7 Duplicate-Gate Promotion Workflow

Date: 2026-06-03

Status: implemented locally; Claude review accepted.

## Purpose

Goal3070 added discovery metadata and `rtdsl.lint_new_primitive(...)`, but the
hard promotion workflow was still split between code and habit. Goal3087 makes
the v2.7 duplicate gate executable in the hierarchy validator and gives future
primitive-promotion reviews a reusable handoff template.

This is governance and metadata work only. It does not authorize release
readiness, public speedup wording, zero-copy wording, broad RT-core claims,
paper-reproduction claims, or app-specific native engine logic.

## Changes

- Added duplicate-gate vocabulary exports:
  - `PRIMITIVE_DUPLICATE_KEY_FAMILIES`
  - `PRIMITIVE_PROMOTION_METADATA_STATUSES`
- Extended `rtdsl.validate_primitive_hierarchy(...)` with a candidate-scoped
  promotion mode:

```python
rtdsl.validate_primitive_hierarchy(
    candidate_tree,
    enforce_promotion_metadata=True,
    promotion_candidate_ids=(candidate_node.id,),
)
```

- The new mode fails closed when a candidate above the promotion status
  threshold shares the duplicate-key facets with an existing primitive and does
  not provide both:
  - `considered_alternatives`
  - `distinct_from`
- The mode requires explicit `promotion_candidate_ids` so old or unrelated
  hierarchy nodes are not reclassified by accident.
- Added a reusable review handoff template:
  - `docs/handoff/HANDOFF_TEMPLATE_PRIMITIVE_PROMOTION_REVIEW.md`
- Refreshed the generated primitive catalog so the guardrail is visible in
  `docs/rtdl_primitive_catalog.md`.

## Validation

Focused validation passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test `
  tests.goal3084_v2_7_primitive_discovery_workflow_docs_test `
  tests.goal3081_v2_7_advisory_planner_test `
  tests.goal3077_v2_7_composition_recipes_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal2624_primitive_hierarchy_test

Ran 42 tests in 1.088s
OK
```

The test suite proves the target D-4 behavior:

- A synthetic near-duplicate candidate fails `lint_new_primitive(...)`.
- The same candidate fails candidate-scoped
  `validate_primitive_hierarchy(..., enforce_promotion_metadata=True, ...)`
  when promotion metadata is missing.
- The same candidate passes after documenting `considered_alternatives` and
  `distinct_from`.
- The gate fails closed if promotion enforcement is requested without a
  candidate scope.
- The gate fails closed if the candidate scope references an unknown node id.
- The generated catalog and promotion handoff template both document the
  search-before-create workflow.

## Boundary

This closes the D-4 duplicate-gate workflow from
`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`
for the current v2.7 metadata/orchestration lane. It is not a stable primitive
promotion, not a performance claim, and not a release packet.

External review from Claude accepted Goal3087. See
`docs/reviews/goal3088_claude_review_goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`.
