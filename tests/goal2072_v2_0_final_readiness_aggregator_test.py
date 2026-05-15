import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2072_v2_0_final_readiness_aggregator.py"
PAYLOAD = ROOT / "docs" / "reports" / "goal2072_v2_0_final_readiness_aggregator.json"
REPORT = ROOT / "docs" / "reports" / "goal2072_v2_0_final_readiness_aggregator_2026-05-15.md"


class Goal2072V20FinalReadinessAggregatorTest(unittest.TestCase):
    def test_script_generates_current_readiness_object(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--output-json",
                "scratch/goal2072_v2_0_final_readiness_aggregator_test.json",
                "--output-md",
                "scratch/goal2072_v2_0_final_readiness_aggregator_test.md",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-2000:])
        payload = json.loads((ROOT / "scratch/goal2072_v2_0_final_readiness_aggregator_test.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal2072")
        self.assertEqual(payload["final_matrix_status"], "final-v2-0-release-matrix-candidate")
        self.assertEqual(payload["pre_release_gate_status"], "pass")

    def test_current_payload_is_blocked_until_claude_and_consensus(self):
        payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "blocked")
        self.assertTrue(payload["external_reviews"]["gemini"]["present"])
        self.assertIn(
            "explicit user-requested release action missing",
            payload["blockers"],
        )
        self.assertFalse(payload["release_claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["release_claim_boundary"]["all_apps_have_measured_v2_speedup"])

    def test_markdown_names_packet_and_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2072 v2.0 Final Readiness Aggregator",
            "final matrix counts",
            "focused gate tests",
            "External Reviews",
            "package_install_claim_authorized",
            "Next Action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
