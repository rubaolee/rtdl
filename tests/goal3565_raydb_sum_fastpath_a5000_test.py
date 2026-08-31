from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3565_raydb_sum_fastpath_a5000"
SUMMARY = ARTIFACT / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3565_raydb_sum_fastpath_a5000_2026-06-06.md"


class Goal3565RayDBSumFastPathA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_sum_fast_path_repairs_raydb_sum_row(self) -> None:
        raydb = self.payload["raydb"]
        summary = raydb["by_mode"]["sum"]
        self.assertEqual(len(summary["values"]["v23"]), 5)
        self.assertEqual(len(summary["values"]["v29"]), 5)
        self.assertGreater(float(summary["v29_speedup_vs_v23"]), 1.5)
        self.assertLess(float(summary["median_metric_sec"]["v29"]), float(summary["median_metric_sec"]["v23"]))

    def test_count_sanity_stays_near_parity(self) -> None:
        count = self.payload["raydb"]["by_mode"]["count"]
        self.assertEqual(len(count["values"]["v23"]), 3)
        self.assertEqual(len(count["values"]["v29"]), 3)
        self.assertGreater(float(count["v29_speedup_vs_v23"]), 0.99)
        self.assertLess(float(count["v29_speedup_vs_v23"]), 1.03)

    def test_artifact_records_generic_fast_path_and_exact_commit(self) -> None:
        self.assertEqual(self.payload["v29_commit"], "bdcf53b313a4782bef38856703a2707d673b00e7")
        fast_path = self.payload["fast_path"]
        self.assertEqual(fast_path["generic_native_fast_path"], "device_column_grouped_i64_small_group_kernel")
        self.assertEqual(fast_path["small_group_capacity_threshold"], 1024)
        self.assertEqual(fast_path["operations"], ["sum", "sum_count"])
        self.assertIs(fast_path["app_specific_native_logic"], False)

    def test_claim_boundaries_remain_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key, value in boundary.items():
            if key == "internal_results_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)

        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not authorize", text)
        self.assertIn("public v2.9 speedup claims", text)
        self.assertIn("app-specific native logic: `False`", text)


if __name__ == "__main__":
    unittest.main()
