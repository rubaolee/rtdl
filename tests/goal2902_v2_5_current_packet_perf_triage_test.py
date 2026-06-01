import json
import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2902_v2_5_current_packet_perf_triage.py"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2902_current_packet_perf_triage_pod"
RAYDB_GATE = (
    ROOT
    / "docs"
    / "reports"
    / "goal2896_pod_artifacts"
    / "goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json"
)
JSON_REPORT = ROOT / "docs" / "reports" / "goal2902_current_packet_perf_triage_2026-05-31.json"
MD_REPORT = ROOT / "docs" / "reports" / "goal2902_current_packet_perf_triage_2026-05-31.md"


class Goal2902V25CurrentPacketPerfTriageTest(unittest.TestCase):
    def test_script_rebuilds_ten_app_triage_from_current_packet(self) -> None:
        output = ROOT / "docs" / "reports" / "_goal2902_test_rebuild.json"
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-dir",
                    str(ARTIFACT_DIR),
                    "--raydb-gate",
                    str(RAYDB_GATE),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("targets=2", completed.stdout)
            data = json.loads(output.read_text(encoding="utf-8"))
        finally:
            output.unlink(missing_ok=True)

        self.assertEqual(data["status"], "pass")
        self.assertEqual(len(data["apps"]), 10)
        self.assertEqual(data["top_priority"], "hausdorff_xhd")
        self.assertEqual(
            [row["app"] for row in data["performance_targets"]],
            ["hausdorff_xhd", "barnes_hut"],
        )
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertEqual(data["source_commit"], "f050d6d51533fed3e32acf19c4668c646236ad5f")
        self.assertEqual(data["claim_boundary_violations"], {})
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_records_current_perf_targets_and_boundaries(self) -> None:
        text = MD_REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2902", text)
        self.assertIn("Hausdorff/X-HD", text)
        self.assertIn("Barnes-Hut", text)
        self.assertIn("RTNN is green", text)
        self.assertIn("not release consensus", text)
        self.assertIn("does not authorize public speedup claims", text)
        self.assertIn("automatic Triton selection", text)

    def test_json_report_matches_fresh_packet_summary(self) -> None:
        data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        packet = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertTrue(packet["all_pass"])
        self.assertEqual(packet["claim_boundary_violations"], {})
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["artifact_count"], 7)
        self.assertEqual(data["source_commit"], packet["source_commit"])

    def test_readiness_indexes_goal2902_as_internal_planning_only(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        report_path = "docs/reports/goal2902_current_packet_perf_triage_2026-05-31.md"

        self.assertEqual(validation["status"], "accept")
        self.assertTrue(packet["required_report_presence"][report_path])
        self.assertIn("use_goal2902_current_packet_perf_triage_for_next_perf_targets", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
