# Goal3102: v2.7 Current Closeout After Semantic Search Preview

Date: 2026-06-03

Status: current v2.7 primitive discovery/orchestration closeout; not a release packet.

## Purpose

Goal3102 updates the v2.7 closeout position after Goal3099 implemented the
previously deferred D-8 item as a bounded preview. It does not rewrite the
Goal3094/3098 historical closeout. Instead, it records the current state:
D-1 through D-8 are now all closed, with D-8 closed only as deterministic,
opt-in, metadata-only semantic search.

## Current Design Item Status

| Item | Design Target | Current Status | Evidence |
| --- | --- | --- | --- |
| D-1 | Add discovery fields to `PrimitiveHierarchyNode` plus controlled facets | Done | Goal3070 / Goal3072 |
| D-2 | Backfill discovery metadata for current stable and candidate nodes | Done | Goal3090 / Goal3093 |
| D-3 | Add `primitive_discovery.py` APIs: `primitive_index`, `find_primitive`, `describe_primitive` | Done | Goal3070 / Goal3072 |
| D-4 | Add duplicate gate and promotion checklist | Done | Goal3087 / Goal3089 |
| D-5 | Generate `docs/rtdl_primitive_catalog.md` from source of truth plus drift test | Done | Goal3073 / Goal3074 |
| D-6 | Add `CompositionRecipe` and recipe discovery | Done | Goal3077 / Goal3078 / Goal3079 |
| D-7 | Add explain-only advisory planner | Done | Goal3081 / Goal3083 |
| D-8 | Optional semantic search over summaries and intent phrases | Done as preview | Goal3099 / Goal3100 / Goal3101 |

## Current Public/Preview Surface

The v2.7 primitive discovery surface now includes:

- `rtdsl.primitive_index()`
- `rtdsl.find_primitive(...)`
- `rtdsl.find_primitive_semantic(..., enable_preview=True)`
- `rtdsl.describe_primitive(...)`
- `rtdsl.lint_new_primitive(candidate_node)`
- `rtdsl.validate_primitive_hierarchy(require_discovery_metadata=True)`
- `rtdsl.validate_primitive_semantic_search()`
- `rtdsl.recipe_index()`
- `rtdsl.find_recipe(...)`
- `rtdsl.describe_recipe(...)`
- `rtdsl.plan_continuation(...)`

The advisory planner and semantic search preview remain non-executing:

- `PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False`
- `PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False`
- `PRIMITIVE_SEMANTIC_SEARCH_EXECUTES = False`
- `PRIMITIVE_SEMANTIC_SEARCH_USES_EMBEDDINGS = False`
- `PRIMITIVE_SEMANTIC_SEARCH_AUTO_PARTNER_SELECTION_ALLOWED = False`

## Current Validation Snapshot

Local validation on 2026-06-03:

```text
strict_hierarchy True
semantic_search True
semantic_executes False
semantic_uses_embeddings False
semantic_auto_partner False
recipes True
planner accept
planner_executes False
planner_auto_partner False
node_count 50
recipe_count 5
```

Focused v2.7 test slice:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3099_v2_7_semantic_search_preview_test tests.goal3094_v2_7_primitive_discovery_orchestration_closeout_test tests.goal3090_v2_7_discovery_metadata_backfill_test tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test tests.goal3084_v2_7_primitive_discovery_workflow_docs_test tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test

Ran 56 tests in 1.190s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

## Consensus State

Historical closeout:

- Goal3094 / Goal3098 recorded 3-AI acceptance for D-1 through D-7, with D-8
  correctly deferred at that time.

Post-D-8 preview:

- Goal3099 implemented D-8 as deterministic metadata-only semantic search.
- Goal3100 Gemini review returned `accept-with-boundary`.
- Goal3101 recorded Codex + Gemini 2-AI consensus.
- Claude was attempted for Goal3099 but was session-limited, so no Claude
  verdict is counted for the D-8 preview.

This means the current v2.7 discovery/orchestration campaign is internally
closed, with D-8 explicitly bounded as preview ergonomics rather than a release
or execution feature.

## What v2.7 Still Does Not Claim

This current closeout does not authorize:

- release readiness;
- public speedup wording;
- zero-copy wording;
- broad RT-core claims;
- paper-reproduction claims;
- stable primitive promotion;
- hidden auto-dispatch;
- hidden auto partner selection;
- app-specific native engine logic;
- ML/embedding-backed semantic search;
- telemetry-backed ranking;
- execution-coupled orchestration.

## Next Reasonable Work

The v2.7 primitive discovery/orchestration lane can stop here unless the user
explicitly asks for more learner ergonomics. Next substantive work should move
back to benchmark-driven v2.x/v3.0 runtime design: device residency,
first-class partner handoff, benchmark primitive hardening, and carefully
reviewed user-extensibility planning.
