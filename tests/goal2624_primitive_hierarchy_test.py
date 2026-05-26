from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2624PrimitiveHierarchyTest(unittest.TestCase):
    def test_hierarchy_validates_dependency_order(self) -> None:
        validation = rt.validate_primitive_hierarchy()

        self.assertTrue(validation["valid"], validation)
        self.assertEqual(
            validation["layer_order"],
            (
                "execution_residency",
                "traversal",
                "row_emission",
                "bounded_materialization",
                "reduction",
                "continuation",
                "candidate_experimental",
            ),
        )
        self.assertGreaterEqual(validation["node_count"], 40)
        self.assertEqual(validation["missing_dependencies"], ())
        self.assertEqual(validation["backward_dependencies"], ())

    def test_core_primitives_are_in_expected_layers(self) -> None:
        expected = {
            "traversal.any_hit": "traversal",
            "traversal.count_hits": "traversal",
            "rows.aabb_range_intersection_rows": "row_emission",
            "materialization.collect_k_bounded": "bounded_materialization",
            "reduction.scalar": "reduction",
            "reduction.grouped": "reduction",
            "continuation.partner_resident": "continuation",
            "candidate.aggregate_frontier_traversal": "candidate_experimental",
        }

        for node_id, layer in expected.items():
            with self.subTest(node_id=node_id):
                node = rt.find_primitive_hierarchy_node(node_id)
                self.assertEqual(node.layer, layer)

    def test_hierarchy_keeps_app_semantics_out_of_engine_nodes(self) -> None:
        forbidden_terms = (
            "dbscan",
            "robot",
            "contact",
            "collision",
            "raydb",
            "rayjoin",
            "rtnn",
            "barnes",
            "sql",
        )
        engine_nodes = [
            node
            for node in rt.iter_primitive_hierarchy_nodes()
            if node.status != "app_or_partner_code"
        ]

        for node in engine_nodes:
            searchable = f"{node.id} {node.title}".lower()
            for term in forbidden_terms:
                with self.subTest(node=node.id, term=term):
                    self.assertNotIn(term, searchable)

        exclusions = " ".join(rt.APP_OWNED_BOUNDARY_EXCLUSIONS).lower()
        self.assertIn("contact", exclusions)
        self.assertIn("dbscan", exclusions)
        self.assertIn("sql", exclusions)

    def test_public_exports_and_serializable_snapshot(self) -> None:
        self.assertIn("primitive_hierarchy", rt.__all__)
        self.assertIn("primitive_layer_map", rt.__all__)
        self.assertIn("validate_primitive_hierarchy", rt.__all__)

        hierarchy = rt.primitive_hierarchy()
        self.assertIsInstance(hierarchy, tuple)
        self.assertEqual(hierarchy[0]["id"], "layer.execution_residency")
        self.assertIn("children", hierarchy[0])

        layer_map = rt.primitive_layer_map()
        self.assertIn("materialization.collect_k_bounded", layer_map["bounded_materialization"])
        self.assertIn("rows.aabb_range_intersection_rows", layer_map["row_emission"])

    def test_catalog_documents_runtime_hierarchy_source_of_truth(self) -> None:
        catalog = (ROOT / "docs" / "rtdl_primitive_catalog.md").read_text(encoding="utf-8")

        self.assertIn("src/rtdsl/primitive_hierarchy.py", catalog)
        self.assertIn("Execution / Residency", catalog)
        self.assertIn("Traversal", catalog)
        self.assertIn("Row Emission", catalog)
        self.assertIn("Bounded Materialization", catalog)
        self.assertIn("Reduction", catalog)
        self.assertIn("Continuation", catalog)
        self.assertIn("Candidate / Experimental", catalog)
        self.assertIn("App semantics are deliberately outside the hierarchy", catalog)


if __name__ == "__main__":
    unittest.main()
