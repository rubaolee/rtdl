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
from goal18_compare_result_modes import compare_goal18
from run_full_verification import run_full_verification
from tests._optional_native_compare import skip_optional_native_compare_failure


ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
_pythonpath_key = next((key for key in ENV if key.upper() == "PYTHONPATH"), "PYTHONPATH")
ENV[_pythonpath_key] = os.pathsep.join(("src", ".", ENV.get(_pythonpath_key, ""))).strip(os.pathsep)


class ReportSmokeTest(unittest.TestCase):
    def test_baseline_runner_missing_workload_reports_usage(self) -> None:
        cp = subprocess.run(
            [sys.executable, "-m", "rtdsl.baseline_runner"],
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
            [sys.executable, "-m", "rtdsl.baseline_runner", "lsi", "--dataset", "__missing_dataset__"],
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
            try:
                artifacts = rt.generate_embree_evaluation_artifacts(
                    workloads=("lsi",),
                    iterations=1,
                    warmup=1,
                    output_dir=Path(tmpdir) / "evaluation",
                )
            except Exception as exc:
                skip_optional_native_compare_failure(exc)
                raise
            payload = json.loads(artifacts["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["suite"], "rtdl_embree_evaluation")
            self.assertGreaterEqual(len(payload["records"]), 1)
            self.assertEqual({record["workload"] for record in payload["records"]}, {"lsi"})
            self.assertTrue(artifacts["pdf"].read_bytes().startswith(b"%PDF-1.4"))

    def test_goal18_compare_smoke_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                payload = compare_goal18(Path(tmpdir) / "goal18", repeats=3)
            except Exception as exc:
                skip_optional_native_compare_failure(exc)
                raise
        self.assertIn("workloads", payload)
        self.assertTrue(payload["workloads"]["lsi"]["raw_matches_dict"])
        self.assertTrue(payload["workloads"]["pip"]["raw_matches_dict"])


if __name__ == "__main__":
    unittest.main()
