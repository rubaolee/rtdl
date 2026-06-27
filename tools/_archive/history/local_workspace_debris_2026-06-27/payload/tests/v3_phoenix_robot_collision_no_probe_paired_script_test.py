from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "v3_phoenix_robot_collision_flag_stream_no_probe_paired.py"


class V3PhoenixRobotCollisionNoProbePairedScriptTest(unittest.TestCase):
    def test_dry_run_records_validation_and_no_probe_commands_without_authorizing_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "robot_no_probe"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output-dir",
                    str(output_dir),
                    "--sample-count",
                    "2",
                    "--timed-repeats",
                    "7",
                    "--timed-warmup",
                    "1",
                    "--validation-repeats",
                    "3",
                    "--validation-warmup",
                    "1",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("dry_run", completed.stdout)
            payload = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["contract"], "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["robot_planning_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertTrue(payload["claim_boundary"]["performance_timing_excludes_probe_reference"])

        commands = payload["planned_commands"]
        self.assertEqual(len(commands), 6)
        validation = [row for row in commands if row["kind"] == "validation"]
        timed = [row for row in commands if row["kind"] == "timed_no_probe"]
        self.assertEqual({row["backend"] for row in validation}, {"embree", "optix"})
        self.assertEqual(len(timed), 4)
        self.assertTrue(all("--no-probe-reference" not in row["command"] for row in validation))
        self.assertTrue(all("--no-probe-reference" in row["command"] for row in timed))
        self.assertIn("CPU probe-reference validation", payload["evidence_protocol"]["validation_rows"])
        self.assertIn("--no-probe-reference", payload["evidence_protocol"]["timed_rows"])

    def test_script_keeps_external_review_gate_explicit(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("review_required_before_m7", text)
        self.assertIn('"m7_promotion_authorized": False', text)
        self.assertIn('"robot_planning_speedup_claim_authorized": False', text)
        self.assertIn('"continuous_collision_claim_authorized": False', text)
        self.assertIn('"exact_solid_collision_claim_authorized": False', text)


if __name__ == "__main__":
    unittest.main()
