import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests.rtdl_sorting_test import native_oracle_available


ROOT = Path(__file__).resolve().parents[1]


class Goal142GenerateOnlyJaccardTest(unittest.TestCase):
    def test_rendered_program_is_specific_to_jaccard_contract(self) -> None:
        source = rt.render_python_program(
            rt.GenerateOnlyRequest(
                workload="polygon_set_jaccard",
                dataset="authored_polygon_set_jaccard_minimal",
                backend="cpu",
                verify=True,
                output_mode="rows",
            )
        )
        self.assertIn('REQUEST_WORKLOAD = "polygon_set_jaccard"', source)
        self.assertIn("generated_polygon_set_jaccard", source)
        self.assertIn("predicate=rt.polygon_set_jaccard(exact=False)", source)
        self.assertIn('REQUEST_DATASET = "authored_polygon_set_jaccard_minimal"', source)
        self.assertIn("return expected_rows == actual_rows", source)

    def test_generated_jaccard_cpu_python_reference_program_runs_and_verifies(self) -> None:
        build_root = ROOT / "build" / "goal142_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_polygon_set_jaccard.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="polygon_set_jaccard",
                    dataset="authored_polygon_set_jaccard_minimal",
                    backend="cpu_python_reference",
                    verify=True,
                    output_mode="rows",
                ),
                output_path,
            )
            completed = subprocess.run(
                [sys.executable, str(output_path)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["workload"], "polygon_set_jaccard")
            self.assertEqual(payload["backend"], "cpu_python_reference")
            self.assertTrue(payload["verified_against_cpu_python_reference"])
            self.assertEqual(
                payload["rows"],
                [
                    {
                        "intersection_area": 5,
                        "jaccard_similarity": 5.0 / 19.0,
                        "left_area": 13,
                        "right_area": 11,
                        "union_area": 19,
                    }
                ],
            )

    def test_generated_jaccard_program_omits_verification_key_when_not_requested(self) -> None:
        build_root = ROOT / "build" / "goal142_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_polygon_set_jaccard_noverify.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="polygon_set_jaccard",
                    dataset="authored_polygon_set_jaccard_minimal",
                    backend="cpu_python_reference",
                    verify=False,
                    output_mode="summary",
                ),
                output_path,
            )
            completed = subprocess.run(
                [sys.executable, str(output_path)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertNotIn("verified_against_cpu_python_reference", payload)
            self.assertEqual(payload["row_count"], 1)

    def test_generate_only_cli_supports_polygon_set_jaccard(self) -> None:
        build_root = ROOT / "build" / "goal142_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "cli_generated_polygon_set_jaccard.py"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rtdl_generate_only.py",
                    "--workload",
                    "polygon_set_jaccard",
                    "--dataset",
                    "authored_polygon_set_jaccard_minimal",
                    "--backend",
                    "cpu_python_reference",
                    "--output-mode",
                    "summary",
                    "--artifact-shape",
                    "single_file",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["request"]["workload"], "polygon_set_jaccard")
            self.assertTrue(output_path.exists())

    @unittest.skipUnless(native_oracle_available(), "Native oracle is not available in the current environment")
    def test_generated_jaccard_cpu_handoff_bundle_runs(self) -> None:
        build_root = ROOT / "build" / "goal142_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            bundle_dir = Path(tmpdir) / "bundle"
            payload = rt.generate_handoff_bundle(
                rt.GenerateOnlyRequest(
                    workload="polygon_set_jaccard",
                    dataset="authored_polygon_set_jaccard_minimal",
                    backend="cpu",
                    verify=True,
                    output_mode="summary",
                    artifact_shape="handoff_bundle",
                ),
                bundle_dir,
            )
            completed = subprocess.run(
                [sys.executable, payload["program"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["backend"], "cpu")
            self.assertTrue(result["verified_against_cpu_python_reference"])
            self.assertEqual(result["row_count"], 1)


if __name__ == "__main__":
    unittest.main()
