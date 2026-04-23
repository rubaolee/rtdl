from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal769_rtx_pod_one_shot.py"


class Goal769RtxPodOneShotTest(unittest.TestCase):
    def test_dry_run_emits_complete_batched_plan(self) -> None:
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            tmp = Path(tmpdir)
            output_json = tmp / "summary.json"
            artifact_json = tmp / "artifact.json"
            artifact_md = tmp / "artifact.md"
            bundle = tmp / "bundle.tgz"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output-json",
                    str(output_json.relative_to(ROOT)),
                    "--artifact-json",
                    str(artifact_json.relative_to(ROOT)),
                    "--artifact-md",
                    str(artifact_md.relative_to(ROOT)),
                    "--bundle-tgz",
                    str(bundle.relative_to(ROOT)),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["suite"], "goal769_rtx_pod_one_shot")
            self.assertEqual(payload["status"], "ok")
            step_names = [step["name"] for step in payload["steps"]]
            self.assertIn("git_fetch", step_names)
            self.assertIn("install_optix_dev_headers", step_names)
            self.assertIn("goal763_bootstrap", step_names)
            self.assertIn("goal761_run_manifest", step_names)
            self.assertIn("goal762_analyze_artifacts", step_names)
            self.assertEqual(payload["artifact_bundle"]["status"], "dry_run")
            self.assertTrue(output_json.exists())


if __name__ == "__main__":
    unittest.main()
