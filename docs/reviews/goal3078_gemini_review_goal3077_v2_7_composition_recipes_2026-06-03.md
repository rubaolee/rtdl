# Goal3078: Gemini Review for Goal3077 v2.7 Advisory Composition Recipes

Date: 2026-06-03

## Review of Goal3077: v2.7 Advisory Composition Recipes

### Context

This review focuses on Goal3077, which introduces advisory composition recipes over existing primitive nodes. This work builds upon Goal3070 (primitive discovery) and Goal3073 (generated primitive catalog). The core idea is to provide discoverability and planning metadata for compositions of primitives, strictly as advisory guidance.

### Review Questions and Verdicts

Here are the answers to the review questions based on the inspection of the provided files:
- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`

**1. Are the new `CompositionRecipe` records genuinely advisory metadata rather than hidden execution/dispatch?**
*   **Verdict:** `accept`
*   **Reasoning:** The `CompositionRecipe` and `CompositionRecipeStep` are `dataclass`es designed purely for data storage. No execution or dispatch logic is present in `primitive_recipes.py`. Explicit `boundary` and `claim_boundary` fields within the recipes, along with `automatic_partner_selection_allowed=False` (which is validated to be `False`), reinforce the advisory nature and prevent any hidden execution.

**2. Do the recipe ids/titles/summaries preserve the app-agnostic primitive boundary?**
*   **Verdict:** `accept`
*   **Reasoning:** The naming conventions and content of recipe IDs (e.g., `recipe.hit_existence_to_count_summary`), titles, and summaries consistently describe compositions of generic primitives. The `boundary` fields within each recipe explicitly state that app-specific logic remains outside the recipe's scope. Unit tests confirm the absence of app-specific forbidden terms in recipe metadata.

**3. Is `find_recipe(...)` deterministic and useful enough for this first composition slice?**
*   **Verdict:** `accept`
*   **Reasoning:** The `find_recipe()` function employs a clear scoring mechanism based on facet matches, aliases, intent phrases, and text, with a deterministic sorting order (by score, then recipe ID). The returned `CompositionRecipeMatch` objects provide sufficient information for an initial discoverability layer.

**4. Does `validate_composition_recipes()` fail closed on missing primitive steps, unknown tags, missing boundaries, or auto partner selection?**
*   **Verdict:** `accept`
*   **Reasoning:** `validate_composition_recipes()` includes robust checks for duplicate IDs, unknown statuses, unknown capability tags, missing primitive steps (by verifying against the primitive hierarchy), recipes that allow automatic partner selection (which are disallowed), and missing boundary definitions. If any of these conditions are met, the validation result explicitly flags them, enforcing a "fail closed" behavior. This is further validated by unit tests.

**5. Does the generated catalog explain recipes without overclaiming partner support, speedups, zero-copy, release readiness, or paper reproduction?**
*   **Verdict:** `accept`
*   **Reasoning:** The `docs/rtdl_primitive_catalog.md` prominently features disclaimers at both the document level and within the "Composition Recipes" section, explicitly stating that it "does not authorize public release wording, public speedup claims," etc. Each recipe's `partner_policy` and `claim_boundary` fields are rendered, reinforcing these disclaimers at a granular level. Unit tests confirm the presence and correct wording of these disclaimers.

**6. Is it acceptable to proceed next to an advisory planner only after this recipe layer stays green?**
*   **Verdict:** `accept`
*   **Reasoning:** The comprehensive design and implementation of the advisory composition recipe layer, coupled with rigorous validation and testing, provide a solid, safe, and explicitly metadata-driven foundation. This ensures that any subsequent advisory planner will operate on well-defined and non-executable metadata, making it entirely acceptable to proceed.

### Conclusion

Goal3077 successfully introduces advisory composition recipes as pure metadata, maintaining clear boundaries and disclaiming any overreaching execution or performance claims. The implementation is robust, well-tested, and aligns with the stated purpose of enhanced discoverability and planning without introducing hidden complexities or unauthorized behavior.
