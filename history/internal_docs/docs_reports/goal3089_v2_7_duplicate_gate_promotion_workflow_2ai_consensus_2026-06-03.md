# Goal3089: 2-AI Consensus For Goal3087 Duplicate-Gate Promotion Workflow

Date: 2026-06-03

Status: accepted with bounded scope.

## Inputs

- Codex implementation/report:
  - `docs/reports/goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`
- Claude independent review:
  - `docs/reviews/goal3088_claude_review_goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`

## Consensus Verdict

Goal3087 is accepted as the current v2.7 executable duplicate-gate workflow for
primitive promotion packets.

Codex and Claude agree that the implemented candidate-scoped validation is the
right shape:

- `lint_new_primitive(candidate_node)` remains the pre-insertion duplicate
  check.
- `validate_primitive_hierarchy(..., enforce_promotion_metadata=True,
  promotion_candidate_ids=(candidate_node.id,))` is now the post-insertion
  promotion gate.
- The gate fails closed when a near-duplicate promotion candidate omits
  `considered_alternatives` and `distinct_from`.
- The gate also fails closed when enforcement is requested without a candidate
  scope or when the requested candidate id is absent from the tree.
- Existing or legacy nodes are not accidentally reclassified because promotion
  enforcement is candidate-scoped and off by default.
- The generated primitive catalog and reusable handoff template now make the
  search-before-create workflow visible and executable.

## Boundaries

Claude noted two design boundaries that are accepted as intentional for this
stage:

- The duplicate threshold requires full duplicate-key family saturation for the
  candidate's declared key families, with a minimum overlap of three facets.
  This limits false positives but does not claim to catch every partial
  near-duplicate.
- `exactness` remains a controlled discovery facet but is not part of
  `PRIMITIVE_DUPLICATE_KEY_FAMILIES`. Exactness alone is not treated as a
  duplicate key.

These are not blockers for Goal3087. Future primitive-promotion reviewers
should still read the `nearest` output and not treat the gate as a semantic
substitute for review judgment.

## Validation

Codex validation:

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

Also passed:

```text
py -3 -m py_compile src\rtdsl\primitive_hierarchy.py src\rtdsl\primitive_catalog.py src\rtdsl\primitive_discovery.py src\rtdsl\__init__.py tests\goal3087_v2_7_duplicate_gate_promotion_workflow_test.py
```

Claude could not run the tests in its sandbox, but performed code-level review
and accepted the implementation. Codex test execution provides the local
runtime evidence.

## Claim Boundary

This consensus does not authorize release readiness, public speedup wording,
zero-copy wording, broad RT-core claims, paper-reproduction claims, stable
primitive promotion, or app-specific native engine logic. It accepts only the
v2.7 duplicate-gate promotion workflow.
