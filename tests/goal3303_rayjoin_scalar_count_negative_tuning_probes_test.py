from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3303_rayjoin_scalar_count_negative_tuning_probes_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3303_prepared_edge_scalar_count_probe_pod_2026-06-04.json"


class Goal3303RayJoinScalarCountNegativeTuningProbesTest(unittest.TestCase):
    def test_report_records_negative_probe_conclusions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "no new default selected",
            "prepared edge layout is slower",
            "crossing-only boundary mode is invalid",
            "129 != 1430",
            "current recommended PIP performance route remains",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_prepared_edge_artifact_remains_claim_blocked_and_slower_than_current_best(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["rtdl_commit"], "56a91c8955985acd2ef98964c776444797b7bce9")
        self.assertEqual(artifact["status"], "pass_with_optimization_gap")
        self.assertFalse(any(artifact["claim_boundary"].values()))
        comparisons = {row["workload"]: row for row in artifact["comparisons"]}
        self.assertEqual(comparisons["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertGreater(comparisons["pip"]["rtdl_over_rayjoin_query_ratio"], 1.5)
        pip = artifact["rtdl"]["pip"]
        self.assertTrue(pip["pip_scalar_count_pipeline"])
        self.assertEqual(pip["device_filtered_boundary_mode"], "inclusive")
        self.assertEqual(pip["counts"]["last"], 1430)
        self.assertGreater(pip["prepared_query_ms"]["median"], 0.40)
        self.assertLess(pip["validation_exact_query_ms"]["median"], 1.0)
        self.assertEqual(pip["native_phase_samples"][0]["mode"], "device_filtered_count")


if __name__ == "__main__":
    unittest.main()
