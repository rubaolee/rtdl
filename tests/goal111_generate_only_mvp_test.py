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


class Goal111GenerateOnlyMvpTest(unittest.TestCase):
    def test_generate_only_rejects_unknown_workload(self) -> None:
        with self.assertRaises(ValueError):
            rt.generate_python_program(
                {
                    "workload": "not_a_workload",
                    "dataset": "authored_segment_polygon_minimal",
                    "backend": "cpu",
                },
                ROOT / "build" / "should_not_exist.py",
            )

    def test_rendered_program_is_specific_to_requested_contract(self) -> None:
        source = rt.render_python_program(
            rt.GenerateOnlyRequest(
                workload="segment_polygon_hitcount",
                dataset="derived/br_county_subset_segment_polygon_tiled_x4",
                backend="cpu",
                verify=True,
                output_mode="summary",
            )
        )
        self.assertIn('REQUEST_WORKLOAD = "segment_polygon_hitcount"', source)
        self.assertIn('REQUEST_DATASET = "derived/br_county_subset_segment_polygon_tiled_x4"', source)
        self.assertIn('REQUEST_BACKEND = "cpu"', source)
        self.assertIn('REQUEST_OUTPUT_MODE = "summary"', source)
        self.assertIn("verified_against_cpu_python_reference", source)
        self.assertIn("generated_segment_polygon_hitcount", source)
        self.assertIn('rt.load_cdb("tests/fixtures/rayjoin/br_county_subset.cdb")', source)
        self.assertIn("tile_segments(case[\"segments\"], copies=4, step_x=30.0, step_y=20.0)", source)

    def test_generated_cpu_python_reference_program_runs_and_verifies(self) -> None:
        build_root = ROOT / "build" / "goal111_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_segment_polygon_hitcount.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_hitcount",
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
            self.assertEqual(payload["workload"], "segment_polygon_hitcount")
            self.assertEqual(payload["dataset"], "authored_segment_polygon_minimal")
            self.assertEqual(payload["backend"], "cpu_python_reference")
            self.assertTrue(payload["verified_against_cpu_python_reference"])
            self.assertEqual(
                payload["rows"],
                [{"segment_id": 1, "hit_count": 1}, {"segment_id": 2, "hit_count": 1}],
            )

    @unittest.skipUnless(native_oracle_available(), "Native oracle is not available in the current environment")
    def test_generated_cpu_program_runs_and_verifies(self) -> None:
        build_root = ROOT / "build" / "goal111_test"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as tmpdir:
            output_path = Path(tmpdir) / "generated_segment_polygon_hitcount_cpu.py"
            rt.generate_python_program(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_hitcount",
                    dataset="authored_segment_polygon_minimal",
                    backend="cpu",
                    verify=True,
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
            self.assertEqual(payload["backend"], "cpu")
            self.assertTrue(payload["verified_against_cpu_python_reference"])
            self.assertEqual(payload["row_count"], 2)


if __name__ == "__main__":
    unittest.main()
