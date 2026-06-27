# External Review Handoff: Goal3090 v2.7 Discovery Metadata Backfill

Please perform a read-only review of Goal3090 and write the review to:

`docs/reviews/goal3091_claude_review_goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`

## Context

Goal3090 closes D-2 from:

`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`

Goal3070 added primitive discovery metadata fields and search APIs. Goal3090
backfills the remaining promotion-status hierarchy nodes and adds strict
metadata validation.

## Files To Inspect

- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_catalog.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3090_v2_7_discovery_metadata_backfill_test.py`
- `docs/reports/goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`

## Validation To Run

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test `
  tests.goal3084_v2_7_primitive_discovery_workflow_docs_test `
  tests.goal3081_v2_7_advisory_planner_test `
  tests.goal3077_v2_7_composition_recipes_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal2624_primitive_hierarchy_test
```

## Review Questions

1. Does `require_discovery_metadata=True` make the D-2 requirement executable
   without changing default hierarchy validation?
2. Are the new tags, aliases, intent phrases, reference paths, and backend
   scopes app-agnostic and conservative?
3. Is `metadata_only` an honest backend marker for abstract layer/overview
   nodes?
4. Does the generated catalog accurately report strict discovery metadata
   validation?
5. Does Goal3090 avoid release, performance, zero-copy, broad RT-core,
   paper-reproduction, and app-specific native-engine claims?

Use one of the accepted verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`. If accepted with a boundary, list required
follow-up fixes separately from optional future work.
