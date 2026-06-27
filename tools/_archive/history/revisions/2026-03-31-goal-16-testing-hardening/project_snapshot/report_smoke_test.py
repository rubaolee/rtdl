import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")

import rtdsl as rt
from run_full_verification import run_full_verification


ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = os.pathsep.join(("src", ".", ENV.get("PYTHONPATH", ""))).strip(os.pathsep)


class ReportSmokeTest(unittest.TestCase):
    def test_baseline_runner_missing_workload_reports_usage(self) -> None:
        cp = subprocess.run(
            ["python3", "-m", "rtdsl.baseline_runner"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=ENV,
            check=False,
        )
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("usage:", cp.stderr.lower())

    def test_baseline_runner_invalid_dataset_reports_error(self) -> None:
        cp = subprocess.run(
            ["python3", "-m", "rtdsl.baseline_runner", "lsi", "--dataset", "__missing_dataset__"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=ENV,
            check=False,
        )
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("unsupported lsi dataset", (cp.stdout or "") + (cp.stderr or ""))

    def test_full_verification_smoke_path(self) -> None:
        payload = run_full_verification(skip_unittest=True)
        self.assertIn("cli", payload)
        self.assertIn("artifacts", payload)
        self.assertIn("embree", payload)

    def test_goal15_artifact_smoke_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = rt.generate_embree_evaluation_artifacts(
                workloads=("lsi",),
                iterations=1,
                warmup=1,
                output_dir=Path(tmpdir) / "evaluation",
            )
            payload = json.loads(artifacts["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["suite"], "rtdl_embree_evaluation")
            self.assertGreaterEqual(len(payload["records"]), 1)
            self.assertEqual({record["workload"] for record in payload["records"]}, {"lsi"})
            self.assertTrue(artifacts["pdf"].read_bytes().startswith(b"%PDF-1.4"))


if __name__ == "__main__":
    unittest.main()
