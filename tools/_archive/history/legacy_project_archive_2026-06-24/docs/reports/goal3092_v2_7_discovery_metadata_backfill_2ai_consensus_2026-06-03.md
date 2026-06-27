# Goal3092: 2-AI Consensus For Goal3090 Discovery Metadata Backfill

Date: 2026-06-03

Status: accepted with bounded scope.

## Inputs

- Codex implementation/report:
  - `docs/reports/goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`
- Claude independent review:
  - `docs/reviews/goal3091_claude_review_goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`

## Consensus Verdict

Goal3090 is accepted as the v2.7 D-2 discovery metadata backfill.

Codex and Claude agree that:

- `require_discovery_metadata=True` makes the D-2 requirement executable without
  changing default hierarchy validation behavior.
- All promotion-status nodes now carry non-empty discovery metadata fields:
  `capability_tags`, `aliases`, `intent_phrases`, `reference_path`, and
  `backends`.
- The backfilled metadata stays app-agnostic and conservative.
- `metadata_only` is an honest backend marker for non-executable overview or
  future-pressure nodes.
- The generated primitive catalog correctly reports strict discovery metadata
  validation as `True` with no missing rows.
- No new runtime primitive, partner choice, performance claim, zero-copy claim,
  release action, or app-specific native engine logic is introduced.

## Optional Future Note

Claude noted a stylistic inconsistency: some layer overview nodes use concrete
backend lists while other overview nodes use `metadata_only`. This is not a
Goal3090 blocker because executable child nodes carry their own backend scopes,
but a future catalog cleanup may either normalize all layer overview rows to
`metadata_only` or explicitly document the convention that a layer row may
summarize child backend scope.

## Validation

Codex validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test `
  tests.goal3084_v2_7_primitive_discovery_workflow_docs_test `
  tests.goal3081_v2_7_advisory_planner_test `
  tests.goal3077_v2_7_composition_recipes_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal2624_primitive_hierarchy_test

Ran 47 tests in 1.047s
OK
```

Also passed:

```text
py -3 -m py_compile src\rtdsl\primitive_hierarchy.py src\rtdsl\primitive_catalog.py src\rtdsl\primitive_discovery.py src\rtdsl\__init__.py tests\goal3090_v2_7_discovery_metadata_backfill_test.py
```

Claude could not execute tests in its environment but performed static review
and accepted the implementation with no required fixes.

## Claim Boundary

This consensus does not authorize release readiness, public speedup wording,
zero-copy wording, broad RT-core claims, paper-reproduction claims, stable
primitive promotion, or app-specific native engine logic. It accepts only the
v2.7 discovery metadata backfill and strict metadata-validation workflow.
