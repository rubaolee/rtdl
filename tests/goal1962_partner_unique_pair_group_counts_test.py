from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1962_partner_unique_pair_group_counts_2026-05-14.md"


class Goal1962PartnerUniquePairGroupCountsTest(unittest.TestCase):
    def test_unique_pair_group_count_primitive_is_public_and_generic(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def partner_group_count_unique_pairs_by_key", adapters)
        self.assertIn("group_keys must be present in output_group_keys", adapters)
        self.assertIn("item_keys must be non-negative", adapters)
        self.assertIn("torch.unique", adapters)
        self.assertIn("cupy.unique", adapters)
        self.assertIn("torch.bincount", adapters)
        self.assertIn("cupy.bincount", adapters)
        self.assertIn("from .partner_adapters import partner_group_count_unique_pairs_by_key", init_text)
        self.assertIn('"partner_group_count_unique_pairs_by_key"', init_text)

    def test_segment_polygon_hitcount_uses_shared_unique_pair_count_wrapper(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def _count_unique_pairs_for_runtime", adapters)
        self.assertIn("partner_group_count_unique_pairs_by_key(", adapters)
        self.assertIn("runtime[\"name\"] in (\"torch\", \"cupy\")", adapters)
        self.assertGreaterEqual(adapters.count("_count_unique_pairs_for_runtime("), 2)
        self.assertNotIn("hit_counts = runtime[\"count_unique_pairs_by_ids\"]", adapters)

    def test_report_and_preflight_record_goal1962(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("partner_group_count_unique_pairs_by_key", report)
        self.assertIn("arbitrary output group IDs", report)
        self.assertIn("generic witness rows", report)
        self.assertIn("no app-specific native reduction", report)
        self.assertIn("tests.goal1962_partner_unique_pair_group_counts_test", preflight)


if __name__ == "__main__":
    unittest.main()
