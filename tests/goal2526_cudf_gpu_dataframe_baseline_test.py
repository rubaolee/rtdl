import json
from importlib import util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2526_cudf_gpu_dataframe_baseline.py"
REPORT = ROOT / "docs/reports/goal2526_cudf_gpu_dataframe_baseline_2026-05-23.md"
ARTIFACT = ROOT / "docs/reports/goal2526_cudf_gpu_dataframe_baseline_pod_2026-05-23.json"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"
GOAL2525_REPORT = ROOT / "docs/reports/goal2525_gpu_database_candidate_gate_2026-05-23.md"


EXPECTED_ROWS = {
    "count": [
        {"region_id": 0, "count": 2},
        {"region_id": 1, "count": 1},
        {"region_id": 2, "count": 1},
    ],
    "sum": [
        {"region_id": 0, "sum": 190},
        {"region_id": 1, "sum": 200},
        {"region_id": 2, "sum": 80},
    ],
    "min": [
        {"region_id": 0, "min": 90},
        {"region_id": 1, "min": 200},
        {"region_id": 2, "min": 80},
    ],
    "max": [
        {"region_id": 0, "max": 100},
        {"region_id": 1, "max": 200},
        {"region_id": 2, "max": 80},
    ],
    "avg_as_sum_count": [
        {"region_id": 0, "sum": 190, "count": 2},
        {"region_id": 1, "sum": 200, "count": 1},
        {"region_id": 2, "sum": 80, "count": 1},
    ],
}


def _load_runner():
    spec = util.spec_from_file_location("goal2526_cudf_gpu_dataframe_baseline", SCRIPT)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal2526CudfGpuDataframeBaselineTest(unittest.TestCase):
    def test_runner_expected_rows_match_contract(self) -> None:
        runner = _load_runner()
        self.assertEqual(runner.expected_rows(), EXPECTED_ROWS)

    def test_pod_artifact_records_cudf_success_and_timing_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "goal2526_cudf_gpu_dataframe_baseline")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["repeats"], 500)
        self.assertTrue(payload["cudf_available"])
        self.assertEqual(payload["cudf_version"], "26.04.000")
        self.assertEqual(payload["cupy_version"], "14.1.0")
        self.assertTrue(payload["all_match_cpu_reference"])
        self.assertEqual(payload["cudf_rows"], EXPECTED_ROWS)
        self.assertEqual(payload["expected_cpu_reference_rows"], EXPECTED_ROWS)
        self.assertGreater(payload["cudf_device_sync_timing_ms"]["median"], 0)
        self.assertGreater(payload["cudf_host_rows_timing_ms"]["median"], 0)
        self.assertGreater(payload["cudf_end_to_end_timing_ms"]["median"], 0)
        self.assertIn("fixture loaded once", payload["input_boundary"])
        self.assertIn("host row materialization", payload["output_boundary"])
        self.assertFalse(payload["performance_claim_authorized"])

    def test_report_and_readme_define_cudf_as_lightweight_gpu_not_dbms(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        goal2525 = GOAL2525_REPORT.read_text(encoding="utf-8")
        for text in (report, readme):
            self.assertIn("RAPIDS/cuDF", text)
            self.assertIn("GPU dataframe", text)
            self.assertIn("not a SQL-engine", text)
        self.assertIn("Goal2526 installs RAPIDS/cuDF", goal2525)
        self.assertIn("does not authorize public speedup", report)
        self.assertIn("4.340234 ms", report)


if __name__ == "__main__":
    unittest.main()
