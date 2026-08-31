from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3077V27CompositionRecipesTest(unittest.TestCase):
    def test_composition_recipes_validate(self) -> None:
        validation = rt.validate_composition_recipes()

        self.assertTrue(validation["valid"], validation)
        self.assertGreaterEqual(validation["recipe_count"], 5)
        self.assertEqual(validation["missing_primitive_steps"], ())
        self.assertEqual(validation["unknown_capability_tags"], ())
        self.assertEqual(validation["automatic_partner_selection_allowed"], ())

    def test_public_exports_include_recipe_api(self) -> None:
        expected = (
            "COMPOSITION_RECIPE_VERSION",
            "COMPOSITION_RECIPES",
            "CompositionRecipe",
            "CompositionRecipeMatch",
            "CompositionRecipeStep",
            "describe_recipe",
            "find_recipe",
            "recipe_index",
            "validate_composition_recipes",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)
                self.assertTrue(hasattr(rt, name))

    def test_recipe_index_is_advisory_and_app_agnostic(self) -> None:
        rows = rt.recipe_index()
        forbidden_title_terms = ("dbscan", "rayjoin", "raydb", "rtnn", "robot", "contact", "sql", "barnes")

        for row in rows:
            with self.subTest(recipe=row["id"]):
                self.assertFalse(row["automatic_partner_selection_allowed"])
                self.assertIn("claim_boundary", row)
                searchable = f"{row['id']} {row['title']} {row['summary']}".lower()
                for term in forbidden_title_terms:
                    self.assertNotIn(term, searchable)

    def test_find_recipe_returns_fixed_radius_ranked_candidate_recipe(self) -> None:
        matches = rt.find_recipe(intent="nearest", shape="fixed_radius", dim="3d", output="grouped")

        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].recipe_id, "recipe.fixed_radius_ranked_candidates")
        self.assertIn("traversal.fixed_radius_count_threshold", matches[0].primitive_ids)
        self.assertIn("rows.fixed_radius_neighbor_rows", matches[0].primitive_ids)
        self.assertIn("continuation.ranked_summary", matches[0].primitive_ids)

    def test_find_recipe_returns_ray_triangle_grouped_summary_by_text(self) -> None:
        matches = rt.find_recipe(text="ray triangle grouped primitive summary")

        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].recipe_id, "recipe.ray_triangle_hit_stream_grouped_summary")
        self.assertIn("never auto-selected", matches[0].partner_policy)

    def test_describe_recipe_exposes_steps_and_boundaries(self) -> None:
        recipe = rt.describe_recipe("recipe.segmented_rows_to_grouped_reduction")
        step_ids = tuple(step["primitive_id"] for step in recipe["steps"])

        self.assertEqual(
            step_ids,
            ("rows.generic_candidate_rows", "continuation.segmented_chunked_rows", "reduction.grouped"),
        )
        self.assertFalse(recipe["automatic_partner_selection_allowed"])
        self.assertIn("does not authorize zero-copy", recipe["claim_boundary"])

    def test_generated_catalog_includes_recipes(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("## Composition Recipes", catalog)
        self.assertIn("recipe.fixed_radius_ranked_candidates", catalog)
        self.assertIn("recipe.ray_triangle_hit_stream_grouped_summary", catalog)
        self.assertIn("They do not execute, dispatch, auto-select partners", catalog)


if __name__ == "__main__":
    unittest.main()
