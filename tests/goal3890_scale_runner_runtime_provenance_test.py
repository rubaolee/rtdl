from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3828_current_benchmark_scale_profile_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3890_scale_runner_runtime_provenance_2026-06-08.md"
A5000_ARTIFACT = ROOT / "docs" / "reports" / "goal3890_scale_runner_runtime_provenance_a5000_dry_run"


class Goal3890ScaleRunnerRuntimeProvenanceTest(unittest.TestCase):
    def test_dry_run_emits_runtime_environment_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "payload.json"
            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        env = payload["runtime_environment"]
        self.assertIn("source_commit", env)
        self.assertIn("source_commit_short", env)
        self.assertIn("git_status_short", env)
        self.assertIn("working_tree_clean", env)
        self.assertIsInstance(env["git_status_short"], list)
        self.assertEqual(env["source_commit_short"], env["source_commit"][:8])
        self.assertIn("python_executable", env)
        self.assertIn("python_version", env)
        self.assertIn("cwd", env)
        self.assertEqual(set(env["rt_library_env"]), {
            "RTDL_OPTIX_LIBRARY",
            "RTDL_OPTIX_LIB",
            "RTDL_EMBREE_LIBRARY",
            "RTDL_HIPRT_LIBRARY",
            "CUDA_VISIBLE_DEVICES",
        })
        self.assertIn("nvidia_smi", env)

        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

    def test_report_documents_provenance_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3890",
            "runtime_environment",
            "source_commit",
            "git_status_short",
            "nvidia-smi",
            "provenance only",
            "does not change any benchmark row command",
            "does not authorize release action",
            "A5000 Dry-Run Evidence",
            "8618467b",
            "working_tree_clean",
        ):
            self.assertIn(phrase, text)

    def test_a5000_dry_run_artifact_records_runtime_environment(self) -> None:
        payload = json.loads((A5000_ARTIFACT / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual((A5000_ARTIFACT / "exit_code").read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(len(payload["rows"]), 1)
        env = payload["runtime_environment"]
        self.assertEqual(env["source_commit_short"], "8618467b")
        self.assertIn("NVIDIA RTX A5000", env["nvidia_smi"])
        self.assertEqual(env["cwd"], "/root/rtdl_goal3876_runner_1780895523")
        self.assertFalse(env["working_tree_clean"])
        self.assertIn(
            "?? docs/reports/goal3890_scale_runner_runtime_provenance_a5000_dry_run/",
            env["git_status_short"],
        )


if __name__ == "__main__":
    unittest.main()
