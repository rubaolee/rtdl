import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2906_current_packet_after_partner_selection_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2906_current_packet_after_partner_selection_pod"
TRIAGE = ROOT / "docs" / "reports" / "goal2906_current_packet_after_partner_selection_triage_2026-05-31.json"


class Goal2906CurrentPacketAfterPartnerSelectionTest(unittest.TestCase):
    def test_packet_passes_cleanly_after_partner_selection(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["artifact_count"], 7)
        self.assertEqual(summary["source_commit"], "1756dce2386cd086aa91edce8e2656ce8d8899f2")
        self.assertEqual(summary["claim_boundary_violations"], {})
        self.assertEqual(summary["dirty_artifacts"], {})

    def test_triage_demotes_barnes_and_rtnn(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual(triage["status"], "pass")
        self.assertEqual(triage["top_priority"], "hausdorff_xhd")
        self.assertEqual([row["app"] for row in triage["performance_targets"]], ["hausdorff_xhd"])
        self.assertEqual(
            apps["barnes_hut"]["performance_status"],
            "current_path_acceptable_with_measured_partner_selection",
        )
        self.assertEqual(apps["barnes_hut"]["selected_vector_sum_partner"], "torch")
        self.assertEqual(
            apps["rtnn"]["performance_status"],
            "current_path_acceptable_near_parity_distribution_dependent",
        )
        self.assertEqual(apps["rtnn"]["near_parity_distributions"], ["uniform"])
        self.assertEqual(apps["rtnn"]["weak_distributions"], [])

    def test_report_records_boundary_and_stability_followup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("7 / 7", text)
        self.assertIn("selected vector-sum partner: `torch`", text)
        self.assertIn("current_path_acceptable_near_parity_distribution_dependent", text)
        self.assertIn("Goal2907 repeat-9 direct probe", text)
        self.assertIn("not a v2.5 release packet", text)


if __name__ == "__main__":
    unittest.main()
