from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1218_v0_9_8_release_authorization_gate as goal1218


ROOT = Path(__file__).resolve().parents[1]


class Goal1218V098ReleaseAuthorizationGateTest(unittest.TestCase):
    def test_gate_evidence_package_review_and_authorization_exist(self) -> None:
        payload = goal1218.build_gate()
        self.assertTrue(payload["valid_gate"], payload)
        self.assertTrue(payload["release_authorized"], payload)
        self.assertFalse(payload["pod_needed_before_authorization"])
        self.assertEqual(payload["version_marker"], "v1.5")
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(
            payload["recommended_next_action"],
            "authorize_release_action",
        )

    def test_current_public_claim_state_remains_bounded(self) -> None:
        payload = goal1218.build_gate()
        public_state = payload["current_public_state"]
        self.assertEqual(public_state["reviewed_public_rtx_wording_rows"], 13)
        self.assertEqual(
            public_state["road_hazard_new_public_row"],
            "road_hazard_screening / prepared_native_compact_summary_40k",
        )
        self.assertEqual(public_state["database_analytics_public_speedup"], "not_reviewed")
        self.assertEqual(public_state["polygon_set_jaccard_public_speedup"], "not_reviewed")

    def test_final_authorization_files_exist_and_no_hardware_blocker_remains(self) -> None:
        payload = goal1218.build_gate()
        missing_package = [row["path"] for row in payload["release_package_files"] if not row["exists"]]
        self.assertEqual(missing_package, [])
        missing_review = [row["path"] for row in payload["release_package_review_files"] if not row["exists"]]
        self.assertEqual(missing_review, [])
        missing_final = [row["path"] for row in payload["final_authorization_files"] if not row["exists"]]
        self.assertEqual(missing_final, [])
        self.assertIn("No additional pod run is required", payload["hardware_evidence_decision"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1218.json"
            output_md = Path(tmpdir) / "goal1218.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1218_v0_9_8_release_authorization_gate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1218 v0.9.8 Release-Authorization Gate", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid_gate"])
            self.assertTrue(payload["release_authorized"])
            self.assertIn("release authorized: `True`", markdown)
            self.assertIn("- none", markdown)
            self.assertIn("pod needed before authorization: `False`", markdown)


if __name__ == "__main__":
    unittest.main()
