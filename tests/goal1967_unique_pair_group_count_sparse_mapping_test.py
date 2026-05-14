from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1967_unique_pair_group_count_sparse_mapping_2026-05-14.md"


class Goal1967UniquePairGroupCountSparseMappingTest(unittest.TestCase):
    def test_unique_pair_group_count_uses_sparse_id_mapping_not_dense_match_matrix(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("torch.searchsorted", adapters)
        self.assertIn("cupy.searchsorted", adapters)
        self.assertIn("sorted_to_original", adapters)
        self.assertIn("group_keys must be present in output_group_keys", adapters)
        self.assertNotIn("output_i64.reshape(-1, 1).eq(group_i64.reshape(1, -1))", adapters)
        self.assertNotIn("output_i64.reshape(-1, 1) == group_i64.reshape(1, -1)", adapters)

    def test_report_and_preflight_record_sparse_mapping_fix(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("sort/searchsorted", report)
        self.assertIn("arbitrary sparse group IDs", report)
        self.assertIn("avoids the old dense", report)
        self.assertIn("tests.goal1967_unique_pair_group_count_sparse_mapping_test", preflight)


if __name__ == "__main__":
    unittest.main()
