from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3304_current_best_rayjoin_same_slice_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3304_current_best_rayjoin_same_slice_pod_2026-06-04.json"


class Goal3304CurrentBestRayJoinSameSliceTest(unittest.TestCase):
    def test_report_keeps_current_best_and_boundary_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "current recommended same-slice RayJoin comparison",
            "pass_with_optimization_gap",
            "device_filtered_validated + inclusive + z_point + scalar count",
            "RayJoin PIP positive count not exposed",
            "not a win",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_current_best_claim_blocked_packet(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["schema"], "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1")
        self.assertEqual(artifact["rtdl_commit"], "c312903ac30ec166432288ada88b145a05cd8eab")
        self.assertEqual(artifact["status"], "pass_with_optimization_gap")
        self.assertFalse(any(artifact["claim_boundary"].values()))

        comparisons = {row["workload"]: row for row in artifact["comparisons"]}
        self.assertEqual(comparisons["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(comparisons["lsi"]["rtdl_count"], 269)
        self.assertLess(comparisons["lsi"]["rtdl_over_rayjoin_query_ratio"], 1.25)

        pip_comparison = comparisons["pip"]
        self.assertEqual(pip_comparison["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertFalse(pip_comparison["rayjoin_positive_assignment_count_available"])
        self.assertEqual(pip_comparison["rtdl_count"], 1430)
        self.assertGreater(pip_comparison["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertLess(pip_comparison["rtdl_over_rayjoin_query_ratio"], 1.6)

        pip = artifact["rtdl"]["pip"]
        self.assertEqual(pip["count_mode"], "device_filtered_validated")
        self.assertEqual(pip["device_filtered_boundary_mode"], "inclusive")
        self.assertEqual(pip["query_axis"], "z_point")
        self.assertTrue(pip["pip_scalar_count_pipeline"])
        self.assertEqual(pip["counts"]["last"], 1430)
        self.assertLess(pip["prepared_query_ms"]["median"], 0.35)
        self.assertLess(pip["validation_exact_query_ms"]["median"], 0.5)
        self.assertEqual(pip["native_phase_samples"][0]["mode"], "device_filtered_count")


if __name__ == "__main__":
    unittest.main()
