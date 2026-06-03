# Goal3090: v2.7 Discovery Metadata Backfill

Date: 2026-06-03

Status: implemented locally; Claude review accepted.

## Purpose

Goal3090 closes the D-2 metadata backfill item from
`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`.

The v2.7 discovery API can only help users and future development agents if
candidate and stable primitive nodes are findable by intent, aliases, reference
paths, and backend scope. Before this goal, 19 promotion-status hierarchy nodes
were still missing discovery metadata. Goal3090 backfills those nodes and makes
the requirement machine-checkable.

This is metadata and documentation work only. It does not authorize release
readiness, public speedup wording, zero-copy wording, broad RT-core claims,
paper-reproduction claims, stable primitive promotion, or app-specific native
engine logic.

## Changes

- Added `PRIMITIVE_DISCOVERY_METADATA_FIELDS`.
- Extended `rtdsl.validate_primitive_hierarchy(...)` with
  `require_discovery_metadata=True`.
- Backfilled conservative discovery metadata for all promotion-status nodes:
  - `capability_tags`
  - `aliases`
  - `intent_phrases`
  - `reference_path`
  - `backends`
- Used `backends=("metadata_only",)` for abstract layer/candidate overview
  nodes that are not executable primitives.
- Refreshed the generated primitive catalog with a strict discovery metadata
  validation snapshot.
- Added `tests/goal3090_v2_7_discovery_metadata_backfill_test.py`.

## Validation

Focused v2.7 validation passed:

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

Ran 47 tests in 1.197s
OK
```

Also passed:

```text
py -3 -m py_compile src\rtdsl\primitive_hierarchy.py src\rtdsl\primitive_catalog.py src\rtdsl\primitive_discovery.py src\rtdsl\__init__.py tests\goal3090_v2_7_discovery_metadata_backfill_test.py
```

The strict audit now reports:

```text
valid True
missing 0
```

for `rtdsl.validate_primitive_hierarchy(require_discovery_metadata=True)`.

## Boundary

Goal3090 improves the metadata quality of the primitive hierarchy. It does not
add a new primitive, change runtime lowering, choose a partner, claim
performance, or move any release gate.

Claude review accepted Goal3090 with no required follow-up fixes. See
`docs/reviews/goal3091_claude_review_goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`.
