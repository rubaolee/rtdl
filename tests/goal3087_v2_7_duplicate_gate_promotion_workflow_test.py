from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
HANDOFF_TEMPLATE = ROOT / "docs" / "handoff" / "HANDOFF_TEMPLATE_PRIMITIVE_PROMOTION_REVIEW.md"


class Goal3087V27DuplicateGatePromotionWorkflowTest(unittest.TestCase):
    def test_candidate_scoped_validation_rejects_near_duplicate_without_metadata(self) -> None:
        base = _reference_fixed_radius_count_node()
        candidate = _candidate_fixed_radius_count_node()

        lint = rt.lint_new_primitive(candidate, existing_nodes=(base,))
        self.assertFalse(lint["valid"], lint)

        validation = rt.validate_primitive_hierarchy(
            (base, candidate),
            enforce_promotion_metadata=True,
            promotion_candidate_ids=(candidate.id,),
        )

        self.assertFalse(validation["valid"], validation)
        self.assertTrue(validation["promotion_metadata_enforced"])
        self.assertEqual(validation["promotion_candidate_ids"], (candidate.id,))
        self.assertEqual(validation["promotion_metadata_missing"][0]["node_id"], candidate.id)
        duplicate_ids = {
            entry["node_id"]
            for entry in validation["promotion_metadata_missing"][0]["possible_duplicates"]
        }
        self.assertIn(base.id, duplicate_ids)

    def test_candidate_scoped_validation_accepts_documented_distinction(self) -> None:
        base = _reference_fixed_radius_count_node()
        candidate = _candidate_fixed_radius_count_node(
            considered_alternatives=(base.id,),
            distinct_from=(
                "Keeps a bounded capacity variant for review; the existing count "
                "primitive remains the default recommendation."
            ),
        )

        lint = rt.lint_new_primitive(candidate, existing_nodes=(base,))
        self.assertTrue(lint["valid"], lint)

        validation = rt.validate_primitive_hierarchy(
            (base, candidate),
            enforce_promotion_metadata=True,
            promotion_candidate_ids=(candidate.id,),
        )

        self.assertTrue(validation["valid"], validation)
        self.assertEqual(validation["promotion_metadata_missing"], ())

    def test_promotion_validation_requires_explicit_candidate_scope(self) -> None:
        validation = rt.validate_primitive_hierarchy(
            (_reference_fixed_radius_count_node(),),
            enforce_promotion_metadata=True,
        )

        self.assertFalse(validation["valid"], validation)
        self.assertTrue(validation["promotion_candidate_scope_required"])

    def test_promotion_validation_rejects_unknown_candidate_id(self) -> None:
        validation = rt.validate_primitive_hierarchy(
            (_reference_fixed_radius_count_node(),),
            enforce_promotion_metadata=True,
            promotion_candidate_ids=("candidate.missing_node",),
        )

        self.assertFalse(validation["valid"], validation)
        self.assertEqual(validation["unknown_promotion_candidate_ids"], ("candidate.missing_node",))

    def test_public_exports_include_duplicate_gate_vocabulary(self) -> None:
        expected = (
            "PRIMITIVE_DUPLICATE_KEY_FAMILIES",
            "PRIMITIVE_PROMOTION_METADATA_STATUSES",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)
                self.assertTrue(hasattr(rt, name))

    def test_catalog_documents_candidate_scoped_gate(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("Promotion metadata enforced by default: `False`", catalog)
        self.assertIn("rtdsl.validate_primitive_hierarchy(..., enforce_promotion_metadata=True", catalog)
        self.assertIn("promotion_candidate_ids=(candidate_id,)", catalog)

    def test_promotion_handoff_template_requires_search_and_gate_outputs(self) -> None:
        text = HANDOFF_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("find_primitive", text)
        self.assertIn("lint_new_primitive(candidate_node)", text)
        self.assertIn("enforce_promotion_metadata=True", text)
        self.assertIn("promotion_candidate_ids", text)
        self.assertIn("considered_alternatives", text)
        self.assertIn("distinct_from", text)


def _reference_fixed_radius_count_node() -> rt.PrimitiveHierarchyNode:
    return rt.PrimitiveHierarchyNode(
        id="traversal.test_fixed_radius_count",
        title="Test Fixed Radius Count",
        layer="traversal",
        status="stable_primitive",
        summary="Synthetic existing fixed-radius count primitive for gate tests.",
        capability_tags=(
            "intent:count",
            "shape:fixed_radius",
            "dim:3d",
            "output:scalar",
            "keying:by_query_id",
        ),
    )


def _candidate_fixed_radius_count_node(
    *,
    considered_alternatives: tuple[str, ...] = (),
    distinct_from: str = "",
) -> rt.PrimitiveHierarchyNode:
    return rt.PrimitiveHierarchyNode(
        id="candidate.test_fixed_radius_count_variant",
        title="Test Fixed Radius Count Variant",
        layer="candidate_experimental",
        status="candidate_behavior",
        summary="Synthetic near-duplicate fixed-radius count candidate for promotion tests.",
        capability_tags=(
            "intent:count",
            "shape:fixed_radius",
            "dim:3d",
            "output:scalar",
            "keying:by_query_id",
        ),
        considered_alternatives=considered_alternatives,
        distinct_from=distinct_from,
    )


if __name__ == "__main__":
    unittest.main()
