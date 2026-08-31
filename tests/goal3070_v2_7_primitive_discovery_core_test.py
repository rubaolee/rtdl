from __future__ import annotations

import unittest

import rtdsl as rt


class Goal3070V27PrimitiveDiscoveryCoreTest(unittest.TestCase):
    def test_hierarchy_validation_includes_discovery_tags(self) -> None:
        validation = rt.validate_primitive_hierarchy()

        self.assertTrue(validation["valid"], validation)
        self.assertEqual(validation["unknown_capability_tags"], ())

    def test_public_exports_include_discovery_api(self) -> None:
        expected = (
            "PrimitiveDiscoveryMatch",
            "describe_primitive",
            "find_primitive",
            "lint_new_primitive",
            "primitive_index",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)
                self.assertTrue(hasattr(rt, name))

    def test_primitive_index_exposes_capability_facets(self) -> None:
        rows = {row["id"]: row for row in rt.primitive_index()}
        fixed_radius = rows["traversal.fixed_radius_count_threshold"]

        self.assertIn("intent:count", fixed_radius["capability_tags"])
        self.assertIn("shape:fixed_radius", fixed_radius["capability_tags"])
        self.assertEqual(fixed_radius["facets"]["intent"], ("count",))
        self.assertIn("optix", fixed_radius["backends"])
        self.assertEqual(fixed_radius["reference_path"], "docs/features/fixed_radius_neighbors/README.md")

    def test_find_primitive_returns_best_fixed_radius_count_match(self) -> None:
        matches = rt.find_primitive(intent="count", shape="fixed_radius", dim="3d", output="scalar")

        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].node_id, "traversal.fixed_radius_count_threshold")
        self.assertGreaterEqual(matches[0].score, 40)
        self.assertIn("intent:count", matches[0].matched_on)

    def test_find_primitive_discovers_ranked_summary_by_plain_text(self) -> None:
        matches = rt.find_primitive(text="nearest ranked summary")

        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].node_id, "continuation.ranked_summary")
        self.assertIn("docs/features/knn_rows/README.md", matches[0].reference_path)

    def test_describe_primitive_includes_promotion_metadata(self) -> None:
        description = rt.describe_primitive("reduction.ray_triangle_primitive_grouped_i64")

        self.assertIn("rows.ray_triangle_hit_stream_3d", description["considered_alternatives"])
        self.assertIn("plain grouped reductions", description["distinct_from"])
        self.assertIn("compose in dependency order", rt.find_primitive(text="primitive grouped reduction")[0].compose_hint)

    def test_duplicate_gate_requires_alternatives_and_distinction(self) -> None:
        candidate = rt.PrimitiveHierarchyNode(
            id="candidate.fixed_radius_scalar_count_duplicate",
            title="Duplicate Fixed Radius Count",
            layer="candidate_experimental",
            status="candidate_behavior",
            summary="A deliberately redundant fixed-radius scalar count proposal.",
            capability_tags=(
                "intent:count",
                "shape:fixed_radius",
                "dim:3d",
                "output:scalar",
                "keying:by_query_id",
            ),
        )

        failed = rt.lint_new_primitive(candidate)
        self.assertFalse(failed["valid"], failed)
        self.assertTrue(failed["possible_duplicates"])
        self.assertIn("considered_alternatives", failed["errors"][0])

        documented_candidate = rt.PrimitiveHierarchyNode(
            id=candidate.id,
            title=candidate.title,
            layer=candidate.layer,
            status=candidate.status,
            summary=candidate.summary,
            capability_tags=candidate.capability_tags,
            considered_alternatives=("traversal.fixed_radius_count_threshold",),
            distinct_from="Uses a different capacity policy; requires review before promotion.",
        )
        passed = rt.lint_new_primitive(documented_candidate)
        self.assertTrue(passed["valid"], passed)
        self.assertTrue(passed["promotion_metadata_present"])


if __name__ == "__main__":
    unittest.main()
