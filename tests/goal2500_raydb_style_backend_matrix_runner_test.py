from importlib import util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2500_raydb_style_backend_matrix.py"
REPORT = ROOT / "docs/reports/goal2500_raydb_style_backend_matrix_runner_2026-05-22.md"


def _load_runner():
    spec = util.spec_from_file_location("goal2500_raydb_style_backend_matrix", SCRIPT)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal2500RaydbStyleBackendMatrixRunnerTest(unittest.TestCase):
    def test_cpu_reference_matrix_runs(self) -> None:
        runner = _load_runner()
        payload = runner.run_matrix(backends=("cpu_python_reference",), repeats=2)
        case = payload["cases"]["cpu_python_reference"]
        self.assertEqual(case["status"], "ok")
        self.assertTrue(case["all_match_cpu_reference"])
        self.assertEqual(set(case["modes"]), {"count", "sum", "min", "max", "avg_as_sum_count"})
        self.assertIn("diagnostic", payload["claim_boundary"])

    def test_native_backend_unavailable_is_recorded_as_skip(self) -> None:
        runner = _load_runner()
        payload = runner.run_matrix(backends=("not_a_backend",), repeats=1)
        case = payload["cases"]["not_a_backend"]
        self.assertEqual(case["status"], "skipped")
        self.assertIn("unsupported backend", case["reason"])

    def test_runner_records_lowering_plan_for_each_mode(self) -> None:
        runner = _load_runner()
        payload = runner.run_matrix(backends=("cpu_python_reference",), repeats=1)
        mode = payload["cases"]["cpu_python_reference"]["modes"]["count"]
        self.assertEqual(mode["lowering_plan"]["backend"], "cpu_python_reference")
        self.assertFalse(mode["lowering_plan"]["true_zero_copy_authorized"])

    def test_report_documents_no_claim_boundary_and_pod_use(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("evidence plumbing only", text)
        self.assertIn("do not authorize public speedup", text)
        self.assertIn("SQL-engine, or DBMS claims", text)
        self.assertIn("CUDA/OptiX pod", text)


if __name__ == "__main__":
    unittest.main()
