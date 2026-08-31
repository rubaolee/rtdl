from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3575_raydb_stats_mode_partner_resident_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3575_raydb_stats_mode_partner_resident_a5000" / "stats.json"
SUITE_SMOKE = ROOT / "docs" / "reports" / "goal3575_raydb_stats_mode_partner_resident_a5000" / "suite_smoke.json"


class Goal3575RaydbStatsModePartnerResidentA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.suite_smoke = json.loads(SUITE_SMOKE.read_text(encoding="utf-8"))

    def test_report_records_scope_and_boundaries(self) -> None:
        self.assertIn("turns the grouped-i64 `stats` path from structural support into a real", self.report)
        self.assertIn("not to paper-shaped RT modes", self.report)
        for boundary in (
            "public speedup",
            "whole-app acceleration",
            "broad RT-core acceleration",
            "true zero-copy",
            "paper reproduction",
            "package-install support",
        ):
            self.assertIn(boundary, self.report)

    def test_a5000_stats_artifact_matches_cpu_reference(self) -> None:
        payload = self.artifact
        self.assertEqual(payload["backend"], "optix_partner_resident_experimental")
        self.assertEqual(payload["mode"], "stats")
        self.assertEqual(payload["row_count"], 960000)
        self.assertIs(payload["matches_cpu_reference"], True)
        self.assertEqual(
            payload["rows"],
            [
                {"count": 240000, "max": 100, "min": 90, "region_id": 0, "sum": 22800000},
                {"count": 120000, "max": 200, "min": 200, "region_id": 1, "sum": 24000000},
                {"count": 120000, "max": 80, "min": 80, "region_id": 2, "sum": 9600000},
            ],
        )

    def test_stats_metadata_is_generic_and_claim_bounded(self) -> None:
        metadata = self.artifact["metadata"]
        self.assertEqual(metadata["operation"], "stats")
        self.assertEqual(metadata["reduction"], "stats")
        self.assertEqual(metadata["semantic_aggregate"], "stats")
        self.assertIs(metadata["generic_stats_abi_used"], True)
        self.assertIs(metadata["fused_native_reduction"], True)
        self.assertEqual(metadata["native_launch_count"], 1)
        self.assertIs(metadata["public_speedup_claim_authorized"], False)
        self.assertIs(metadata["true_zero_copy_authorized"], False)
        self.assertLess(metadata["timings"]["query_median_sec"], 0.001)

    def test_full_partner_resident_mode_smoke_stays_coherent(self) -> None:
        payload = self.suite_smoke
        self.assertEqual(payload["backend"], "optix_partner_resident_experimental")
        self.assertEqual(payload["copies"], 1000)
        self.assertIs(payload["all_match_cpu_reference"], True)
        modes = payload["modes"]
        self.assertEqual(
            set(modes),
            {"count", "sum", "min", "max", "stats", "avg_as_sum_count"},
        )
        for mode, result in modes.items():
            with self.subTest(mode=mode):
                self.assertIs(result["matches_cpu_reference"], True)
                self.assertEqual(result["metadata"]["native_launch_count"], 1)
                self.assertIn(mode, self.report)
        stats = modes["stats"]["metadata"]
        self.assertEqual(stats["operation"], "stats")
        self.assertIs(stats["generic_stats_abi_used"], True)
        self.assertIs(stats["fused_native_reduction"], True)
        self.assertIs(stats["public_speedup_claim_authorized"], False)
        self.assertIs(stats["true_zero_copy_authorized"], False)


if __name__ == "__main__":
    unittest.main()
