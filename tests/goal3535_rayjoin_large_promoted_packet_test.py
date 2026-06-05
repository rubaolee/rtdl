from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3535_rayjoin_large_promoted_packet.py"


class Goal3535RayJoinLargePromotedPacketTest(unittest.TestCase):
    def test_dry_run_generates_square_grid_cdb_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = pathlib.Path(tmpdir) / "artifacts"
            output = artifact_dir / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--grid",
                    "4",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-1000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
            left = pathlib.Path(payload["generated_pair"]["left_cdb"])
            right = pathlib.Path(payload["generated_pair"]["right_cdb"])
            self.assertTrue(left.exists())
            self.assertTrue(right.exists())
            self.assertEqual(payload["generated_pair"]["shape_count_per_side"], 16)
        self.assertEqual(payload["schema"], "rtdl.goal3535.rayjoin_large_promoted_packet.v1")
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_script_reuses_goal3532_promoted_packet(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "goal3532_rayjoin_promoted_contract_packet.py",
            "generated_dataset_not_rayjoin_paper_input",
            "shape_count_per_side",
            "public_speedup_claim_authorized",
            "missing promoted-row metrics",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
