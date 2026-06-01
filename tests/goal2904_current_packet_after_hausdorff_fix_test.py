import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2904_current_packet_after_hausdorff_fix_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2904_current_packet_after_hausdorff_fix_pod"
TRIAGE = ROOT / "docs" / "reports" / "goal2904_current_packet_after_hausdorff_fix_triage_2026-05-31.json"


class Goal2904CurrentPacketAfterHausdorffFixTest(unittest.TestCase):
    def test_packet_passes_cleanly_after_hausdorff_fix(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["artifact_count"], 7)
        self.assertEqual(summary["source_commit"], "b6cc4591a0d475489a7cdddb9c15d32aa852afbc")
        self.assertEqual(summary["claim_boundary_violations"], {})
        self.assertEqual(summary["dirty_artifacts"], {})

    def test_triage_demotes_hausdorff_to_near_parity(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual(triage["status"], "pass")
        self.assertEqual(triage["top_priority"], "barnes_hut")
        self.assertEqual([row["app"] for row in triage["performance_targets"]], ["barnes_hut"])
        self.assertEqual(apps["hausdorff_xhd"]["performance_status"], "current_path_acceptable_near_parity")
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.10)
        self.assertIn("reduced_nearest_witness", apps["hausdorff_xhd"]["route"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("7 / 7", text)
        self.assertIn("19.119x", text)
        self.assertIn("1.067x", text)
        self.assertIn("Barnes-Hut", text)
        self.assertIn("not release consensus", text)
        self.assertIn("does not authorize public speedup claims", text)


if __name__ == "__main__":
    unittest.main()
