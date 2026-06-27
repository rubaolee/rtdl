import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_major_performance_mandate_gate.py"
JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_major_performance_mandate_gate_2026-06-22.json"


class V3PhoenixMajorPerformanceMandateGateTest(unittest.TestCase):
    def _run_gate(self, *extra_args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *extra_args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_major_performance_mandate_blocks_current_v3_release(self):
        payload = self._run_gate()

        self.assertEqual(payload["tool"], "v3_phoenix_major_performance_mandate_gate")
        self.assertEqual(payload["status"], "redo_required")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(
            payload["blocking_reasons"],
            [
                "broad_v2x_performance_not_proven",
                "serious_all_app_paired_evidence_failed_release_bar",
                "current_scoped_13_row_surface_not_v3_major_release",
            ],
        )
        self.assertTrue(all(payload["checks"].values()))
        self.assertIn("1.012x", payload["evidence"]["current_same_rt_geomean_summary"])
        self.assertEqual(payload["evidence"]["serious_same_rt_same_metric_comparison_count"], 52)
        self.assertFalse(payload["evidence"]["serious_same_rt_release_consideration_eligible"])
        self.assertEqual(
            payload["evidence"]["serious_same_rt_release_bar"]["missing_promoted_apps"],
            [],
        )
        self.assertIn("generic runtime redesign", payload["evidence"]["required_next_evidence"])

    def test_major_performance_mandate_can_write_json_and_records_decision_audit(self):
        payload = self._run_gate("--pretty", "--json-out", str(JSON_OUT))
        self.assertTrue(JSON_OUT.exists())
        saved = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "redo_required")

        audit = payload["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("Yes.", audit["was_i_foolish"])
        self.assertIn("major version", audit["decision"])
        self.assertIn("all-app", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()
