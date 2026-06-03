from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3090V27DiscoveryMetadataBackfillTest(unittest.TestCase):
    def test_strict_discovery_metadata_validation_passes(self) -> None:
        validation = rt.validate_primitive_hierarchy(require_discovery_metadata=True)

        self.assertTrue(validation["valid"], validation)
        self.assertTrue(validation["discovery_metadata_required"])
        self.assertEqual(validation["discovery_metadata_missing"], ())

    def test_every_promotion_status_node_has_discovery_fields(self) -> None:
        required_fields = rt.PRIMITIVE_DISCOVERY_METADATA_FIELDS

        for node in rt.iter_primitive_hierarchy_nodes():
            if node.status not in rt.PRIMITIVE_PROMOTION_METADATA_STATUSES:
                continue
            for field in required_fields:
                with self.subTest(node=node.id, field=field):
                    self.assertTrue(getattr(node, field), f"{node.id} missing {field}")

    def test_backfilled_nodes_are_discoverable_by_user_intent(self) -> None:
        cases = (
            ("prepared scene reuse", "execution.prepared_rt_state"),
            ("fail closed overflow capacity", "execution.capacity_overflow_contract"),
            ("row schema validation", "materialization.row_schema_validation"),
            ("integer count sum reductions", "reduction.reduce_int"),
            ("columnar grouped aggregate", "reduction.columnar_compact_summary"),
            ("aggregate frontier rows", "rows.aggregate_frontier_collect"),
            ("device resident row stream", "candidate.zero_copy_row_streams"),
        )

        for text, expected_id in cases:
            with self.subTest(text=text):
                matches = rt.find_primitive(text=text)
                self.assertTrue(matches, text)
                self.assertEqual(matches[0].node_id, expected_id)

    def test_catalog_records_strict_discovery_metadata_snapshot(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("Strict discovery metadata validation valid: `True`", catalog)
        self.assertIn("Strict discovery metadata missing: `-`", catalog)

    def test_public_exports_include_discovery_metadata_fields(self) -> None:
        self.assertIn("PRIMITIVE_DISCOVERY_METADATA_FIELDS", rt.__all__)
        self.assertEqual(
            rt.PRIMITIVE_DISCOVERY_METADATA_FIELDS,
            ("capability_tags", "aliases", "intent_phrases", "reference_path", "backends"),
        )


if __name__ == "__main__":
    unittest.main()
