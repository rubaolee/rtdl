# Goal3094: v2.7 Primitive Discovery And Orchestration Closeout

Date: 2026-06-03

Status: closeout packet; Claude review accepted; not a release packet.

## Purpose

Goal3094 closes the main v2.7 primitive discovery and orchestration campaign
that started from:

`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`

The campaign goal was not to add new runtime kernels. It was to make the
existing generic primitive system discoverable, auditable, and harder to grow
redundantly: users and future development agents should search the primitive
surface before proposing new primitives, inspect recipes before composing apps,
and receive explain-only continuation advice without hidden partner routing.

## Design Item Status

| Item | Design Target | Status | Evidence |
| --- | --- | --- | --- |
| D-1 | Add discovery fields to `PrimitiveHierarchyNode` plus controlled facets | Done | Goal3070 / Goal3072 |
| D-2 | Backfill discovery metadata for current stable and candidate nodes | Done | Goal3090 / Goal3093 |
| D-3 | Add `primitive_discovery.py` APIs: `primitive_index`, `find_primitive`, `describe_primitive` | Done | Goal3070 / Goal3072 |
| D-4 | Add duplicate gate and promotion checklist | Done | Goal3087 / Goal3089 |
| D-5 | Generate `docs/rtdl_primitive_catalog.md` from source of truth plus drift test | Done | Goal3073 / Goal3074 |
| D-6 | Add `CompositionRecipe` and recipe discovery | Done | Goal3077 / Goal3078 / Goal3079 |
| D-7 | Add explain-only advisory planner | Done | Goal3081 / Goal3083 |
| D-8 | Optional embedding/semantic search over summaries and intent phrases | Deferred | Explicitly optional in source design; not needed for current deterministic metadata search |

## Current User/Agent Surface

The v2.7 surface now includes:

- `rtdsl.primitive_index()`
- `rtdsl.find_primitive(...)`
- `rtdsl.describe_primitive(...)`
- `rtdsl.lint_new_primitive(candidate_node)`
- `rtdsl.validate_primitive_hierarchy(require_discovery_metadata=True)`
- `rtdsl.recipe_index()`
- `rtdsl.find_recipe(...)`
- `rtdsl.describe_recipe(...)`
- `rtdsl.plan_continuation(...)`

The planner remains advisory only:

- `PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False`
- `PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False`

This preserves the v2.6/v2.7 rule that partner choice is explicit user/runtime
metadata, not hidden dispatch.

## Current Validation Snapshot

Local validation on 2026-06-03:

```text
strict_hierarchy True
recipes True
planner accept
planner_executes False
auto_partner False
node_count 50
recipe_count 5
```

Focused v2.7 test slice:

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

Ran 47 tests
OK
```

## Consensus State

- Goal3070 discovery core: Codex + Gemini accepted.
- Goal3073 generated catalog: Codex + Gemini accepted.
- Goal3077 composition recipes: Codex + Gemini + Claude accepted.
- Goal3081 advisory planner: Codex + Gemini + Claude accepted.
- Goal3084 learner discovery workflow: Codex + Claude accepted.
- Goal3087 duplicate-gate promotion workflow: Codex + Claude accepted.
- Goal3090 discovery metadata backfill: Codex + Claude + Gemini accepted.

## What v2.7 Does Not Claim

This closeout does not authorize:

- release readiness;
- public speedup wording;
- zero-copy wording;
- broad RT-core claims;
- paper-reproduction claims;
- stable primitive promotion;
- hidden auto-dispatch;
- hidden auto partner selection;
- app-specific native engine logic.

## Next Reasonable Work

If v2.7 continues, the only remaining item from the original design is D-8:
optional fuzzy/embedding-style semantic search behind a flag. That should stay
secondary. The deterministic metadata search, recipe discovery, advisory
planner, strict metadata validation, generated catalog, and duplicate gate are
already enough for the current v2.7 governance objective.

Future runtime/performance work should remain in the benchmark-driven v2.x/v3.0
lanes rather than being smuggled into the metadata discovery layer.

Claude accepted this closeout in
`docs/reviews/goal3095_claude_review_goal3094_v2_7_discovery_orchestration_closeout_2026-06-03.md`.
