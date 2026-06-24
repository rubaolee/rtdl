# Handoff: External Review For Goal3077 v2.7 Advisory Composition Recipes

Please perform a read-only external review of Goal3077.

## Context

Goal3070 added primitive discovery. Goal3073 made the primitive catalog
generated from the Python hierarchy. Goal3077 adds advisory composition recipes
over existing primitive nodes.

Primary reports:

- `docs/reports/goal3070_v2_7_primitive_discovery_core_2026-06-03.md`
- `docs/reports/goal3073_v2_7_generated_primitive_catalog_and_drift_gate_2026-06-03.md`
- `docs/reports/goal3077_v2_7_advisory_composition_recipes_2026-06-03.md`

Files to inspect:

- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`

## Review Questions

1. Are the new `CompositionRecipe` records genuinely advisory metadata rather than hidden execution/dispatch?
2. Do the recipe ids/titles/summaries preserve the app-agnostic primitive boundary?
3. Is `find_recipe(...)` deterministic and useful enough for this first composition slice?
4. Does `validate_composition_recipes()` fail closed on missing primitive steps, unknown tags, missing boundaries, or auto partner selection?
5. Does the generated catalog explain recipes without overclaiming partner support, speedups, zero-copy, release readiness, or paper reproduction?
6. Is it acceptable to proceed next to an advisory planner only after this recipe layer stays green?

## Expected Output

Use verdicts from this set only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If you are Gemini, write:

- `docs/reviews/goal3078_gemini_review_goal3077_v2_7_composition_recipes_2026-06-03.md`

If you are Claude, write:

- `docs/reviews/goal3079_claude_review_goal3077_v2_7_composition_recipes_2026-06-03.md`

Do not edit source files. If you run tests, record the exact command and result.
