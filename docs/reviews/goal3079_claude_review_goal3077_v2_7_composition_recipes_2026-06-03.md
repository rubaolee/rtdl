# Goal3079: Claude External Review — Goal3077 v2.7 Advisory Composition Recipes

Date: 2026-06-03

Reviewer: Claude Sonnet 4.6 (external read-only review)

Verdict: **accept-with-boundary**

---

## Files Reviewed

- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md` (generated catalog, recipes section)
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`
- `docs/reports/goal3077_v2_7_advisory_composition_recipes_2026-06-03.md`
- `docs/reports/goal3073_v2_7_generated_primitive_catalog_and_drift_gate_2026-06-03.md`
- `docs/reports/goal3070_v2_7_primitive_discovery_core_2026-06-03.md`

Test run recorded in the goal report:

```
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test

Ran 25 tests in 0.029s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

This reviewer performed a static read-only code inspection. Tests were not independently re-executed.

---

## Q1: Are the new `CompositionRecipe` records genuinely advisory metadata rather than hidden execution/dispatch?

**Yes.**

`CompositionRecipe` and `CompositionRecipeStep` are frozen dataclasses with no callable methods beyond `to_dict()`. The module-level constant
`COMPOSITION_RECIPE_AUTO_PARTNER_SELECTION_ALLOWED = False` is the default for every recipe and is validated by `validate_composition_recipes()`. The API surface (`find_recipe`, `recipe_index`, `describe_recipe`) returns only frozen dataclasses or plain dicts. There is no dispatch method, no executor binding, no engine coupling, and no `__call__` anywhere in `primitive_recipes.py`.

`CompositionRecipeStep` contains only `primitive_id: str`, `role: str`, `phase: str`, `required: bool`, and `notes: str` — all metadata fields, not callables.

The test `test_recipe_index_is_advisory_and_app_agnostic` asserts `assertFalse(row["automatic_partner_selection_allowed"])` for every recipe in the index, providing a runtime enforcement gate for this property.

**Finding: genuinely advisory metadata. No hidden execution or dispatch.**

---

## Q2: Do the recipe ids/titles/summaries preserve the app-agnostic primitive boundary?

**Yes.**

All five recipe ids, titles, and summaries use generic geometric and computational concepts:

| Recipe | Geometry concept | App semantics in title/summary? |
| --- | --- | --- |
| `recipe.hit_existence_to_count_summary` | generic hit predicate | None |
| `recipe.fixed_radius_ranked_candidates` | fixed-radius spatial | None |
| `recipe.ray_triangle_hit_stream_grouped_summary` | ray/triangle geometry | None |
| `recipe.aabb_candidate_rows_to_refinement` | AABB range | None |
| `recipe.segmented_rows_to_grouped_reduction` | generic row streams | None |

The test `test_recipe_index_is_advisory_and_app_agnostic` validates programmatically that the concatenation of `id + title + summary` contains none of the forbidden domain terms: `dbscan`, `rayjoin`, `raydb`, `rtnn`, `robot`, `contact`, `sql`, `barnes`.

One recipe (`recipe.ray_triangle_hit_stream_grouped_summary`) has `evidence_paths=("examples/v2_0/research_benchmarks/raydb_style/README.md",)`. The string `raydb` appears only in this path field, not in the recipe's searchable identity fields (id, title, summary). The test correctly does not flag this.

Each recipe's `boundary` field explicitly names what remains app-owned (e.g., "Caller-owned interpretation of the hit predicate stays outside the recipe", "Exact refinement and domain scoring remain caller-owned").

**Finding: app-agnostic boundary preserved throughout.**

---

## Q3: Is `find_recipe(...)` deterministic and useful enough for this first composition slice?

**Yes, with one minor observation.**

The function is deterministic: it iterates `COMPOSITION_RECIPES` (a fixed immutable tuple) in a fixed order, applies a consistent scoring scheme (facet match +10, alias hit +7, intent-phrase hit +5, body text hit +2), and sorts results by `(-score, recipe_id)` — a stable lexicographic tiebreak. The normalization helpers (`_normalize_token`, `_normalize_text`) are pure functions with no side effects.

The scoring hierarchy is well-calibrated: controlled facet hits (+10) dominate alias hits (+7), which dominate phrase hits (+5), which dominate generic text hits (+2). This matches the parallel design in `primitive_discovery.find_primitive()`, providing consistent discovery behavior across primitives and recipes.

The test `test_find_recipe_returns_fixed_radius_ranked_candidate_recipe` confirms that a four-facet query (`intent=nearest`, `shape=fixed_radius`, `dim=3d`, `output=grouped`) correctly ranks `recipe.fixed_radius_ranked_candidates` first with a score of 40, well ahead of any competing recipe.

**Minor observation:** The `_text_hits` helper uses substring containment (`normalized in query or query in normalized`), so a short query like `text="count"` would match any recipe that has "count" in its id, title, summary, or `intent:count` capability tag. With only five recipes, this is acceptable noise. As the recipe catalog grows, a minimum query-token length or field-weighted body scoring should be considered to avoid overly broad text matches.

**Finding: deterministic and adequate for the first five-recipe slice. Noise from short text queries is acceptable at this scale.**

---

## Q4: Does `validate_composition_recipes()` fail closed on missing primitive steps, unknown tags, missing boundaries, or auto partner selection?

**Yes, on all four.**

Examining `validate_composition_recipes()` in `primitive_recipes.py:356-407`:

| Failure mode | How it fails closed |
| --- | --- |
| Missing primitive steps | Calls `find_primitive_hierarchy_node(step.primitive_id)`; catches `KeyError`; appends to `missing_primitive_steps`; contributes to `valid=False` |
| Unknown capability tags | Set-difference against `PRIMITIVE_CAPABILITY_TAGS`; contributes to `valid=False` |
| Missing boundaries | Checks `not (recipe.partner_policy and recipe.claim_boundary and recipe.boundary)` — requires all three non-empty; contributes to `valid=False` |
| Auto partner selection | Any recipe with `automatic_partner_selection_allowed=True` is collected and contributes to `valid=False` |

The `valid` key is the conjunction of all five zero-checks (duplicate ids, unknown statuses, unknown tags, missing primitive steps, auto partner selection, missing boundaries). A single violation in any category yields `valid=False`.

Confirming the current recipes pass: the primitive IDs in all recipes were traced against the hierarchy:
- `traversal.any_hit` ✓ (`primitive_hierarchy.py:176`)
- `traversal.count_hits` ✓ (`primitive_hierarchy.py:202`)
- `traversal.fixed_radius_count_threshold` ✓ (`primitive_hierarchy.py:256`)
- `traversal.aabb_range_intersects` ✓ (`primitive_hierarchy.py:244`)
- `rows.ray_triangle_hit_stream_3d` ✓ (`primitive_hierarchy.py:302`)
- `rows.fixed_radius_neighbor_rows` ✓ (`primitive_hierarchy.py:359`)
- `rows.aabb_range_intersection_rows` ✓ (`primitive_hierarchy.py:330`)
- `rows.generic_candidate_rows` ✓ (`primitive_hierarchy.py:291`)
- `reduction.ray_triangle_primitive_grouped_i64` ✓ (`primitive_hierarchy.py:590`)
- `reduction.grouped` ✓ (`primitive_hierarchy.py:518`)
- `continuation.segmented_chunked_rows` ✓ (`primitive_hierarchy.py:668`)
- `continuation.ranked_summary` ✓ (`primitive_hierarchy.py:695`)

All capability tags used in recipes were traced against `PRIMITIVE_CAPABILITY_TAGS` in `primitive_hierarchy.py:29-63` — all present.

**Finding: fails closed on all four listed failure modes. Validation is complete and correct.**

---

## Q5: Does the generated catalog explain recipes without overclaiming partner support, speedups, zero-copy, release readiness, or paper reproduction?

**No overclaiming found.**

The generated catalog recipe section (`primitive_catalog.py:279-330`, rendered to `docs/rtdl_primitive_catalog.md:314-336`) opens with:

> "Recipes are advisory composition metadata over existing primitive nodes.
> They do not execute, dispatch, auto-select partners, or authorize
> performance claims."

Each recipe row in the catalog renders its `claim_boundary` field:

| Recipe | Claim boundary |
| --- | --- |
| `hit_existence_to_count_summary` | "this is not a whole-app speedup claim" |
| `fixed_radius_ranked_candidates` | "no ANN or paper-reproduction claim is implied" |
| `ray_triangle_hit_stream_grouped_summary` | "Not SQL, not a paper-system reproduction, and not a broad RT-core or whole-app claim" |
| `aabb_candidate_rows_to_refinement` | "no broad overlay, GIS, or whole-app claim is implied" |
| `segmented_rows_to_grouped_reduction` | "does not authorize zero-copy or performance wording" |

The catalog's overall `## Claim Boundary` section reiterates:

> "This catalog does not authorize release readiness, public speedup wording,
> zero-copy claims, broad RT-core claims, paper-reproduction claims, or
> app-specific native engine logic."

The test `test_generated_catalog_includes_recipes` asserts that the phrase
"They do not execute, dispatch, auto-select partners" appears verbatim in the
generated catalog file, providing a drift gate for this wording.

The `partner_policy` fields consistently use "Primitive-first" as the leading phrase and state that partners are "advisory only", "caller selected", or "never auto-selected" — no auto-partner promotion language anywhere.

**Finding: catalog explains recipes conservatively with no overclaiming on any axis.**

---

## Q6: Is it acceptable to proceed next to an advisory planner only after this recipe layer stays green?

**Yes.**

The architecture is well-sequenced:
1. Goal3070: primitive nodes discoverable by facet (the vocabulary)
2. Goal3073: catalog generated from Python hierarchy + drift gate (the integrity lock)
3. Goal3077: advisory recipes over existing primitives (the composition index)
4. Future: advisory planner that consumes recipes

The recipe layer creates a stable, immutable advisory surface — `COMPOSITION_RECIPES` is a frozen tuple of frozen dataclasses. A planner that reads recipes cannot mutate them, and the `validate_composition_recipes()` + catalog drift gates give the planner a guaranteed-clean input if the CI suite stays green.

The key architectural invariant is that recipes do not execute. A planner built on top of this layer can make planning decisions (select, combine, order) without accidentally inheriting execution coupling from the recipe layer, because no such coupling exists.

The progression makes sense: the recipe layer is the minimal advisory surface a planner needs before it can reason about composition sequences. Blocking planner work until this layer stays green prevents a planner from being built against an unstable recipe substrate.

**Finding: sequencing to advisory planner is sound. Proceed once this recipe layer passes review.**

---

## Boundary Note (Basis for `accept-with-boundary`)

The recipe validation (`validate_composition_recipes`) confirms that each step's `primitive_id` exists in the hierarchy, but does not check the referenced primitive's `status`. As a result, an `advisory_recipe` may reference primitives with status `candidate_behavior` or `internal_generic_path`:

- `recipe.aabb_candidate_rows_to_refinement` → `traversal.aabb_range_intersects` (`internal_generic_path`)
- `recipe.aabb_candidate_rows_to_refinement` → `rows.aabb_range_intersection_rows` (`internal_generic_path`)
- `recipe.ray_triangle_hit_stream_grouped_summary` → `rows.ray_triangle_hit_stream_3d` (`candidate_behavior`)
- `recipe.ray_triangle_hit_stream_grouped_summary` → `reduction.ray_triangle_primitive_grouped_i64` (`candidate_behavior`)

This is intentional design: recipe advisory status is decoupled from the stability of the referenced primitives. The recipe layer itself has no claim to stability beyond its metadata advisory role.

**However:** when a planner is built to surface these recipes to callers, it must propagate per-step primitive stability so callers understand that following a recipe may involve `candidate_behavior` or `internal_generic_path` nodes. The planner should not allow `advisory_recipe` status to implicitly promote the stability of its component steps. This is a design constraint on the _next_ goal, not a defect in this one.

**This recipe layer is clean. The boundary note is forward guidance for the planner goal.**

---

## Summary

| Review question | Finding |
| --- | --- |
| Q1 Advisory metadata, no execution/dispatch | Pass |
| Q2 App-agnostic ids/titles/summaries | Pass |
| Q3 `find_recipe()` deterministic and useful | Pass (minor text-noise note) |
| Q4 `validate_composition_recipes()` fails closed | Pass |
| Q5 Catalog no overclaiming | Pass |
| Q6 Safe to proceed to advisory planner | Yes |

**Verdict: `accept-with-boundary`**

The recipe layer is correct and clean. The single boundary condition carries forward to the planner goal: a planner surfacing recipes to callers must expose per-step primitive status, not allow `advisory_recipe` label to implicitly promote the stability of `candidate_behavior` or `internal_generic_path` steps.
