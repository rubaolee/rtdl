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
            self.assertFalse(payload["artifact_bundle"]["include_deferred"])
            step_names = [step["name"] for step in payload["steps"]]
            self.assertIn("git_fetch", step_names)
            self.assertIn("install_optix_dev_headers", step_names)
            self.assertIn("goal763_bootstrap", step_names)
            self.assertIn("goal761_run_manifest", step_names)
            self.assertIn("goal762_analyze_artifacts", step_names)
            self.assertEqual(payload["artifact_bundle"]["status"], "dry_run")
            self.assertTrue(output_json.exists())

    def test_dry_run_can_batch_deferred_and_only_filters(self) -> None:
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
                    "--include-deferred",
                    "--only",
                    "service_coverage_gaps",
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
            self.assertTrue(payload["include_deferred"])
            self.assertEqual(payload["only"], ["service_coverage_gaps"])
            self.assertTrue(payload["artifact_bundle"]["include_deferred"])
            manifest_step = next(step for step in payload["steps"] if step["name"] == "goal761_run_manifest")
            command = manifest_step["result"]["command"]
            self.assertIn("--include-deferred", command)
            self.assertIn("service_coverage_gaps", command)

    def test_bundle_includes_deferred_manifest_outputs_when_requested(self) -> None:
        report_path = ROOT / "docs" / "reports" / "goal887_hausdorff_threshold_rtx.json"
        if report_path.exists():
            self.skipTest(f"test would overwrite existing artifact: {report_path}")
        report_path.write_text('{"fixture": "deferred"}\n', encoding="utf-8")
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        "from scripts.goal769_rtx_pod_one_shot import _tar_reports; "
                        "base=_tar_reports(Path('build/test_bundle.tgz'), "
                        "dry_run=True, include_deferred=False)['member_count']; "
                        "full=_tar_reports(Path('build/test_bundle.tgz'), "
                        "dry_run=True, include_deferred=True)['member_count']; "
                        "print(base, full)"
                    ),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            base, full = [int(part) for part in completed.stdout.strip().split()]
            self.assertGreater(full, base)
        finally:
            report_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
