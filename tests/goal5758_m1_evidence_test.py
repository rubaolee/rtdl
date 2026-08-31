from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5758M1EvidenceTests(unittest.TestCase):
    def test_create_only_evidence_and_independent_recount(self):
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            output = temp / "evidence"
            archive = temp / "evidence.tar.gz"
            twin = temp / "evidence_twin.tar.gz"
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/goal5758_run_m1_evidence.py"),
                 "--output-root", str(output), "--archive", str(archive),
                 "--twin", str(twin)],
                cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertEqual(archive.read_bytes(), twin.read_bytes())
            result = json.loads((output / "RESULT.json").read_text(encoding="utf-8"))
            self.assertEqual(result["local_pipeline_pass_count"], 3)
            self.assertEqual(result["behavioral_gpu_lane_count"], 0)
            self.assertTrue(result["particle_v1_unchanged"])
            self.assertFalse(result["claim_boundary"]["three_lanes_supported_now_claimed"])

            recount = subprocess.run(
                [sys.executable, str(ROOT / "scripts/goal5758_recount_m1_evidence.py"),
                 str(archive)], cwd=ROOT, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            self.assertEqual(recount.returncode, 0, recount.stdout)
            payload = json.loads(recount.stdout)
            self.assertEqual(payload["manifest_mismatch_count"], 0)
            self.assertEqual(payload["lane_match_count"], 3)
            self.assertEqual(payload["lane_count"], 3)

            with tarfile.open(archive, "r:gz") as handle:
                names = {item.name for item in handle.getmembers() if item.isfile()}
            self.assertIn("goal5758_m1_local_evidence/MANIFEST.json", names)
            self.assertNotIn(".codex", "\n".join(names).lower())

    def test_goal5757_frozen_verifier_still_passes(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/goal5757_verify_core_freeze.py")],
            cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout)


if __name__ == "__main__":
    unittest.main()
