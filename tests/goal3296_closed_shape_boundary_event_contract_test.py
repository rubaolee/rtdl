from __future__ import annotations

import math
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3296_closed_shape_boundary_event_contract_2026-06-04.md"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3296ClosedShapeBoundaryEventContractTest(unittest.TestCase):
    def test_reference_oracle_emits_deterministic_first_crossing_rows(self) -> None:
        points = (
            rt.Point(id=10, x=0.0, y=0.0),
            rt.Point(id=20, x=2.0, y=0.0),
        )
        shapes = (
            rt.Polygon(
                id=7,
                vertices=((-1.0, -1.0), (1.0, -1.0), (1.0, 2.0), (-1.0, 2.0)),
            ),
        )

        rows = rt.point_closed_shape_first_boundary_crossing_2d_cpu(points, shapes)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["point_id"], 10)
        self.assertEqual(row["shape_id"], 7)
        self.assertEqual(row["boundary_id"], 3)
        self.assertEqual(row["event_kind"], 1)
        self.assertTrue(math.isclose(float(row["crossing_t"]), 2.0))
        self.assertTrue(math.isclose(float(row["crossing_x"]), 0.0))
        self.assertTrue(math.isclose(float(row["crossing_y"]), 2.0))

    def test_boundary_event_typed_stream_schema_is_generic_and_non_authorizing(self) -> None:
        fields = (
            "point_id",
            "shape_id",
            "boundary_id",
            "crossing_t",
            "crossing_x",
            "crossing_y",
            "event_kind",
        )

        contract = rt.make_v2_8_geometry_relation_typed_stream_contract(fields, 3)
        metadata = contract.to_metadata()
        producer = rt.make_v2_8_geometry_relation_typed_producer_metadata(fields, 3)

        self.assertEqual(rt.validate_typed_result_stream_contract(contract)["status"], "accept")
        self.assertEqual(metadata["producer_primitive"], "point_closed_shape_first_boundary_crossing_2d")
        self.assertEqual(metadata["column_names"], fields)
        self.assertEqual(producer["schema_id"], "point_closed_shape_boundary_event_2d_columns")
        self.assertFalse(producer["release_authorized"])
        self.assertFalse(producer["rt_core_speedup_claim_authorized"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])

    def test_primitive_discovery_finds_boundary_event_contract_without_app_terms(self) -> None:
        matches = rt.find_primitive(text="first boundary crossing event for closed shape point probes")

        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, "rows.point_closed_shape_boundary_event_columns")
        description = rt.describe_primitive("rows.point_closed_shape_boundary_event_columns")
        searchable = " ".join(
            str(value)
            for value in (
                description["id"],
                description["title"],
                description["summary"],
                description["boundary"],
                description["aliases"],
                description["intent_phrases"],
            )
        ).lower()
        self.assertNotIn("rayjoin", searchable)
        self.assertIn("rows.expanded_aabb_point_membership_rows", description["considered_alternatives"])
        self.assertIn("representative boundary event", description["distinct_from"])

    def test_recipe_is_candidate_only_and_keeps_classification_outside_engine(self) -> None:
        recipes = {
            recipe["id"]: recipe
            for recipe in rt.recipe_index()
        }
        recipe = recipes["recipe.point_closed_shape_boundary_event_selection"]

        self.assertEqual(recipe["status"], "candidate_recipe")
        self.assertFalse(recipe["automatic_partner_selection_allowed"])
        primitive_ids = tuple(step["primitive_id"] for step in recipe["steps"])
        self.assertEqual(
            primitive_ids,
            ("traversal.closest_hit", "rows.point_closed_shape_boundary_event_columns"),
        )
        self.assertIn("caller-owned", recipe["boundary"])
        self.assertIn("does not authorize release", recipe["claim_boundary"])

    def test_catalog_and_report_record_boundary_without_native_claim(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("rows.point_closed_shape_boundary_event_columns", catalog)
        self.assertIn("recipe.point_closed_shape_boundary_event_selection", catalog)
        for phrase in (
            "CPU reference oracle",
            "No native OptiX ABI was added",
            "does not authorize release",
            "does not authorize RT-core speedup wording",
            "RayJoin-specific native logic added: false",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
