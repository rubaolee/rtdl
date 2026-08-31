from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3081V27AdvisoryPlannerTest(unittest.TestCase):
    def test_advisory_planner_validates(self) -> None:
        validation = rt.validate_primitive_advisory_planner()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["executes"])
        self.assertFalse(validation["automatic_partner_selection_allowed"])
        self.assertTrue(validation["recipe_validation_valid"])
        self.assertEqual(validation["errors"], ())

    def test_public_exports_include_planner_api(self) -> None:
        expected = (
            "PRIMITIVE_ADVISORY_PLANNER_VERSION",
            "PRIMITIVE_ADVISORY_PLANNER_EXECUTES",
            "PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED",
            "PrimitiveAdvisoryPlan",
            "PrimitivePartnerOption",
            "PrimitivePlanStep",
            "plan_continuation",
            "validate_primitive_advisory_planner",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)
                self.assertTrue(hasattr(rt, name))

    def test_count_query_recommends_primitive_first_without_partner(self) -> None:
        plans = rt.plan_continuation(intent="count", shape="generic", output="scalar")

        self.assertGreater(len(plans), 0)
        plan = plans[0]
        self.assertEqual(plan.recipe_id, "recipe.hit_existence_to_count_summary")
        self.assertEqual(plan.recommendation, "primitive_first")
        self.assertEqual(plan.partner_options, ())
        self.assertIsNone(plan.selected_partner)
        self.assertFalse(plan.executes)
        self.assertFalse(plan.automatic_partner_selection_allowed)
        self.assertIn("stable_primitive", plan.step_statuses)

    def test_fixed_radius_query_lists_explicit_partner_options_without_selection(self) -> None:
        plans = rt.plan_continuation(
            intent="nearest",
            shape="fixed_radius",
            dim="3d",
            output="grouped",
            partner="numba",
        )

        self.assertGreater(len(plans), 0)
        plan = plans[0]
        options = tuple(option.to_dict() for option in plan.partner_options)
        option_pairs = {(option["operation"], option["partner"], option["status"]) for option in options}

        self.assertEqual(plan.recipe_id, "recipe.fixed_radius_ranked_candidates")
        self.assertEqual(plan.recommendation, "primitive_first_with_explicit_partner_options")
        self.assertEqual(plan.requested_partner, "numba")
        self.assertIsNone(plan.selected_partner)
        self.assertTrue(plan.requires_explicit_partner_choice)
        self.assertIn(("grouped_argmin_f64", "python_reference", "reference_contract"), option_pairs)
        self.assertIn(("grouped_argmin_f64", "triton", "preview_not_promoted"), option_pairs)
        self.assertIn(("grouped_argmin_f64", "numba", "unsupported_fail_closed"), option_pairs)
        self.assertTrue(any("selected_partner remains None" in warning for warning in plan.warnings))

    def test_planner_exposes_non_stable_step_statuses(self) -> None:
        plan = rt.plan_continuation(recipe_id="recipe.ray_triangle_hit_stream_grouped_summary")[0]
        step_rows = tuple(step.to_dict() for step in plan.primitive_steps)
        status_by_id = {step["primitive_id"]: step["primitive_status"] for step in step_rows}

        self.assertIn("rows.ray_triangle_hit_stream_3d", status_by_id)
        self.assertEqual(status_by_id["rows.ray_triangle_hit_stream_3d"], "candidate_behavior")
        self.assertIn("rows.ray_triangle_hit_stream_3d", plan.non_stable_step_ids)
        self.assertIn("does_not_promote", plan.status_boundary)
        self.assertTrue(any("non-stable primitive steps" in warning for warning in plan.warnings))

    def test_catalog_documents_advisory_planner(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("## Advisory Planner", catalog)
        self.assertIn("rtdsl.plan_continuation", catalog)
        self.assertIn("selected_partner=None", catalog)
        self.assertIn("Auto-selects partners | `False`", catalog)


if __name__ == "__main__":
    unittest.main()
