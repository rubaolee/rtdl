# Goal3077: v2.7 Advisory Composition Recipes

Date: 2026-06-03

Status: implemented locally, pending external review.

## Purpose

Goal3070 made individual primitives discoverable. Goal3073 made the primitive
catalog generated from the Python hierarchy. The next v2.7 need is composition:
many user intents are not single primitives, but ordered use of existing
primitive nodes.

Goal3077 adds advisory composition recipes. They are discoverability and
planning metadata only.

## What Changed

Added `src/rtdsl/primitive_recipes.py` with:

- `CompositionRecipeStep`
- `CompositionRecipe`
- `CompositionRecipeMatch`
- `COMPOSITION_RECIPES`
- `recipe_index()`
- `find_recipe(...)`
- `describe_recipe(recipe_id)`
- `validate_composition_recipes()`

Exported the recipe API from `rtdsl.__all__`.

Regenerated `docs/rtdl_primitive_catalog.md` so it now includes a generated
`Composition Recipes` section.

Added `tests/goal3077_v2_7_composition_recipes_test.py`.

## Initial Recipes

The first recipe set is intentionally app-agnostic:

| Recipe | Purpose |
| --- | --- |
| `recipe.hit_existence_to_count_summary` | Compose hit predicates and scalar hit counts when witness rows are not needed. |
| `recipe.fixed_radius_ranked_candidates` | Compose fixed-radius counts, bounded neighbor rows, and ranked summaries by query id. |
| `recipe.ray_triangle_hit_stream_grouped_summary` | Compose ray/triangle hit streams and grouped reductions over caller-owned keys. |
| `recipe.aabb_candidate_rows_to_refinement` | Compose AABB predicates and candidate rows before caller-owned exact refinement. |
| `recipe.segmented_rows_to_grouped_reduction` | Compose segmented row paging and grouped reductions for large row streams. |

## Boundary

Recipes do not:

- execute;
- dispatch;
- auto-select partners;
- change native engine ABI;
- promote app-specific semantics into the engine;
- authorize release readiness;
- authorize speedup, zero-copy, broad RT-core, or paper-reproduction claims.

Every recipe has `automatic_partner_selection_allowed=False`, a partner policy,
a claim boundary, and an app-ownership boundary.

## Verification

Ran on Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 25 tests in 0.029s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Also ran:

```powershell
$env:PYTHONPATH='src;.'; py -3 scripts/generate_rtdl_primitive_catalog.py --check
py -3 -m py_compile src/rtdsl/primitive_recipes.py src/rtdsl/primitive_catalog.py src/rtdsl/__init__.py tests/goal3077_v2_7_composition_recipes_test.py
```

Results: catalog up to date; compile clean.
