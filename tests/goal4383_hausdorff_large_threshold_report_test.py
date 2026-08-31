from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4383_hausdorff_large_threshold_2026-06-14.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal4383_hausdorff_large_threshold_2026-06-14"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal4383HausdorffLargeThresholdReportTest(unittest.TestCase):
    def test_large_threshold_rows_are_same_contract_and_oracle_checked(self) -> None:
        for name in ("embree_c262144_r2.json", "optix_c262144_r2.json"):
            payload = _load(name)
            self.assertEqual(payload["point_count_a"], 1_048_576)
            self.assertEqual(payload["point_count_b"], 1_048_576)
            self.assertEqual(payload["optix_summary_mode"], "directed_threshold_prepared")
            self.assertEqual(payload["hausdorff_threshold"], 0.25)
            self.assertFalse(payload["within_threshold"])
            self.assertTrue(payload["matches_oracle"])
            self.assertTrue(payload["native_continuation_active"])
            self.assertEqual(
                payload["directed_a_to_b"]["generic_primitive"],
                "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            )

    def test_large_row_has_seconds_level_query_and_rt_core_speedup(self) -> None:
        embree = _load("embree_c262144_r2.json")
        optix = _load("optix_c262144_r2.json")

        embree_query = embree["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        optix_query = optix["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        self.assertGreater(embree_query, 8.0)
        self.assertGreater(optix_query, 5.0)
        self.assertGreater(embree_query / optix_query, 1.5)
        self.assertFalse(optix["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_keeps_exact_hausdorff_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("1,048,576 points per side", text)
        self.assertIn("8.74s Embree vs 5.52s OptiX", text)
        self.assertIn("not exact Hausdorff nearest-witness computation", text)
        self.assertIn("not full X-HD paper reproduction", text)


if __name__ == "__main__":
    unittest.main()
