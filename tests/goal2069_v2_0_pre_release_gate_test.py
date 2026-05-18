import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2069_v2_0_pre_release_gate.py"
PAYLOAD = ROOT / "docs" / "reports" / "goal2069_v2_0_pre_release_gate.json"
REPORT = ROOT / "docs" / "reports" / "goal2069_v2_0_pre_release_gate_2026-05-15.md"


class Goal2069V20PreReleaseGateTest(unittest.TestCase):
    def test_script_can_run_full_gate(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--run-tests",
                "--output-json",
                "scratch/goal2069_v2_0_pre_release_gate_test.json",
                "--output-md",
                "scratch/goal2069_v2_0_pre_release_gate_test.md",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-4000:])
        payload = json.loads((ROOT / "scratch/goal2069_v2_0_pre_release_gate_test.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["claim_scan_status"], "pass")
        self.assertEqual(payload["gate_tests"]["status"], "pass")

    def test_reported_gate_blocks_release(self):
        payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["final_matrix_status"], "final-v2-0-release-matrix-candidate")
        self.assertEqual(payload["mixed_apps"], [])
        self.assertFalse(payload["release_claim_boundary"]["v2_0_release_authorized"])
        self.assertTrue(payload["release_claim_boundary"]["all_apps_have_measured_v2_speedup"])
        self.assertTrue(payload["release_claim_boundary"]["all_current_optix_rt_rows_have_measured_v2_speedup"])
        self.assertIn("final v2.0 3-AI release consensus missing", payload["remaining_blockers"])

    def test_markdown_names_deferred_lanes(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "explicitly named v2.0 pre-release gate",
            "not a v2.0 release authorization",
            "Goal2025 Triton/Numba",
            "Goal2037 Embree CPU partner",
            "v3.0 custom engine extensions",
            "focused unittest summary: `40 tests, 1 skipped`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
