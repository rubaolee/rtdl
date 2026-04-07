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


class Goal129GenerateOnlySecondWorkloadTest(unittest.TestCase):
    def test_rendered_program_is_specific_to_anyhit_contract(self) -> None:
        source = rt.render_python_program(
            rt.GenerateOnlyRequest(
                workload="segment_polygon_anyhit_rows",
                dataset="derived/br_county_subset_segment_polygon_tiled_x4",
                backend="cpu",
                verify=True,
                output_mode="summary",
            )
        )
        self.assertIn('REQUEST_WORKLOAD = "segment_polygon_anyhit_rows"', source)
        self.assertIn("generated_segment_polygon_anyhit_rows", source)
        self.assertIn("predicate=rt.segment_polygon_anyhit_rows(exact=False)", source)
        self.assertIn(
            'rt.compare_baseline_rows("segment_polygon_anyhit_rows", expected_rows, actual_rows)',
            source,
        )
        self.assertIn('REQUEST_DATASET = "derived/br_county_subset_segment_polygon_tiled_x4"', source)
        self.assertIn('raise SystemExit("generated program verification failed")', source)

    def test_generated_anyhit_cpu_python_reference_program_runs_and_verifies(self) -> None:
        build_root = ROOT / "build" / "goal129_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_segment_polygon_anyhit_rows.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_anyhit_rows",
                    dataset="authored_segment_polygon_minimal",
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
            self.assertEqual(payload["workload"], "segment_polygon_anyhit_rows")
            self.assertEqual(payload["backend"], "cpu_python_reference")
            self.assertTrue(payload["verified_against_cpu_python_reference"])
            self.assertEqual(
                payload["rows"],
                [{"polygon_id": 10, "segment_id": 1}, {"polygon_id": 11, "segment_id": 2}],
            )

    def test_generated_anyhit_program_omits_verification_key_when_not_requested(self) -> None:
        build_root = ROOT / "build" / "goal129_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_segment_polygon_anyhit_rows_noverify.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_anyhit_rows",
                    dataset="authored_segment_polygon_minimal",
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
            self.assertEqual(payload["row_count"], 2)

    @unittest.skipUnless(native_oracle_available(), "Native oracle is not available in the current environment")
    def test_generated_anyhit_cpu_handoff_bundle_runs(self) -> None:
        build_root = ROOT / "build" / "goal129_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            bundle_dir = Path(tmpdir) / "bundle"
            payload = rt.generate_handoff_bundle(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_anyhit_rows",
                    dataset="authored_segment_polygon_minimal",
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
            self.assertEqual(result["row_count"], 2)
            readme_text = (bundle_dir / "README.md").read_text(encoding="utf-8")
            self.assertNotIn("/Users/rl2025/", readme_text)
            self.assertNotIn("Goal 113", readme_text)


if __name__ == "__main__":
    unittest.main()
