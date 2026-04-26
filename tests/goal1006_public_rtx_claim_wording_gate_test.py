from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1006PublicRtxClaimWordingGateTest(unittest.TestCase):
    def test_gate_is_stricter_than_goal1005_candidates(self) -> None:
        module = __import__(
            "scripts.goal1006_public_rtx_claim_wording_gate",
            fromlist=["build_gate"],
        )
        payload = module.build_gate()
        self.assertEqual(payload["row_count"], 17)
        self.assertEqual(payload["public_review_ready_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertEqual(payload["current_public_wording_source"], "rtdsl.rtx_public_wording_matrix()")
        self.assertIn("does not authorize public speedup claims", payload["boundary"])

    def test_only_service_coverage_is_public_review_ready_now(self) -> None:
        module = __import__(
            "scripts.goal1006_public_rtx_claim_wording_gate",
            fromlist=["build_gate"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_gate()["rows"]
        }
        self.assertEqual(
            rows[("service_coverage_gaps", "prepared_gap_summary")]["public_wording_status"],
            "public_review_ready_query_phase_claim",
        )
        self.assertIn(
            "not a whole-app speedup claim",
            rows[("service_coverage_gaps", "prepared_gap_summary")]["allowed_public_wording"],
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["public_wording_status"],
            "candidate_but_needs_larger_scale_repeat",
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["current_public_wording_status"],
            "public_wording_blocked",
        )
        self.assertEqual(
            rows[("event_hotspot_screening", "prepared_count_summary")]["public_wording_status"],
            "not_public_speedup_candidate",
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1006.json"
            output_md = Path(tmpdir) / "goal1006.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1006_public_rtx_claim_wording_gate.py",
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
            self.assertIn("Goal1006 Public RTX Claim Wording Gate", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["public_review_ready_count"], 1)
            self.assertIn("rtdsl.rtx_public_wording_matrix()", output_md.read_text(encoding="utf-8"))
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
