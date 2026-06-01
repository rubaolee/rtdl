import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2908_current_packet_after_repeat9_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2908_current_packet_after_repeat9_pod"
TRIAGE = ROOT / "docs" / "reports" / "goal2908_current_packet_after_repeat9_triage_2026-05-31.json"


class Goal2908CurrentPacketAfterRepeat9Test(unittest.TestCase):
    def test_packet_passes_cleanly_after_hausdorff_repeat9_default(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["artifact_count"], 7)
        self.assertEqual(summary["source_commit"], "f101b4da0fa088c76ed30711e5b32b1984a411da")
        self.assertEqual(summary["claim_boundary_violations"], {})
        self.assertEqual(summary["dirty_artifacts"], {})

    def test_triage_closes_hausdorff_and_keeps_rtnn_as_followup(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual(triage["status"], "pass")
        self.assertEqual(triage["top_priority"], "rtnn")
        self.assertEqual([row["app"] for row in triage["performance_targets"]], ["rtnn"])
        self.assertEqual(apps["hausdorff_xhd"]["performance_status"], "current_path_acceptable")
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.0)
        self.assertEqual(
            apps["barnes_hut"]["performance_status"],
            "current_path_acceptable_with_measured_partner_selection",
        )
        self.assertEqual(apps["rtnn"]["weak_distributions"], ["clustered"])

    def test_report_records_boundary_and_goal2909_followup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("7 / 7", text)
        self.assertIn("RTDL/CuPy ratio: `0.993x`", text)
        self.assertIn("Goal2909 immediately probes", text)
        self.assertIn("not a v2.5 release packet", text)


if __name__ == "__main__":
    unittest.main()
