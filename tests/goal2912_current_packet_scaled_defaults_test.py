import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2912_current_packet_scaled_defaults_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2912_current_packet_scaled_defaults_pod"
TRIAGE = ROOT / "docs" / "reports" / "goal2912_current_packet_scaled_defaults_triage_2026-05-31.json"


class Goal2912CurrentPacketScaledDefaultsTest(unittest.TestCase):
    def test_packet_passes_cleanly_at_current_scaled_defaults(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["artifact_count"], 7)
        self.assertEqual(summary["source_commit"], "cf3a479d7f40c36df1b3f44f68de20ef1b098221")
        self.assertEqual(summary["claim_boundary_violations"], {})
        self.assertEqual(summary["dirty_artifacts"], {})

    def test_triage_has_no_current_performance_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual(triage["status"], "pass")
        self.assertEqual(triage["performance_targets"], [])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual(apps["rtnn"]["performance_status"], "current_path_acceptable")
        self.assertGreater(apps["rtnn"]["min_cupy_over_rtdl_ratio"], 1.0)
        self.assertEqual(apps["hausdorff_xhd"]["performance_status"], "current_path_acceptable")
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.0)
        self.assertEqual(apps["rt_dbscan"]["performance_status"], "current_path_acceptable")
        self.assertEqual(
            apps["barnes_hut"]["performance_status"],
            "current_path_acceptable_with_measured_partner_selection",
        )

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("performance targets: none", text)
        self.assertIn("CuPy/RTDL ratios: uniform `1.150x`", text)
        self.assertIn("RTDL/CuPy ratio `0.940x`", text)
        self.assertIn("not a v2.5 release authorization", text)


if __name__ == "__main__":
    unittest.main()
