import json
from pathlib import Path
import math
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_fixture_knn_rows_case
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal205KnnRowsCpuOracleTest(unittest.TestCase):
    def test_lowering_supports_knn_rows(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(knn_rows_reference))
        self.assertEqual(plan.workload_kind, "knn_rows")
        self.assertEqual(plan.accel_kind, "native_loop")
        self.assertEqual(plan.emit_fields, ("query_id", "neighbor_id", "distance", "neighbor_rank"))

    def test_run_cpu_matches_python_reference_on_authored_case(self) -> None:
        case = make_knn_rows_authored_case()
        native_rows = rt.run_cpu(knn_rows_reference, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(len(native_rows), len(python_rows))
        for native_row, python_row in zip(native_rows, python_rows):
            self.assertEqual(native_row["query_id"], python_row["query_id"])
            self.assertEqual(native_row["neighbor_id"], python_row["neighbor_id"])
            self.assertEqual(native_row["neighbor_rank"], python_row["neighbor_rank"])
            self.assertTrue(math.isclose(native_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))

    def test_run_cpu_matches_python_reference_on_fixture_case(self) -> None:
        case = make_fixture_knn_rows_case()
        native_rows = rt.run_cpu(knn_rows_reference, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(len(native_rows), len(python_rows))
        self.assertTrue(native_rows)
        for native_row, python_row in zip(native_rows, python_rows):
            self.assertEqual(native_row["query_id"], python_row["query_id"])
            self.assertEqual(native_row["neighbor_id"], python_row["neighbor_id"])
            self.assertEqual(native_row["neighbor_rank"], python_row["neighbor_rank"])
            self.assertTrue(math.isclose(native_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))

    def test_baseline_runner_cpu_backend_supports_knn_rows(self) -> None:
        payload = rt.run_baseline_case(
            knn_rows_reference,
            "authored_knn_rows_minimal",
            backend="cpu",
        )
        self.assertEqual(payload["workload"], "knn_rows")
        self.assertIn("cpu_rows", payload)
        self.assertEqual(tuple(row["neighbor_rank"] for row in payload["cpu_rows"][:3]), (1, 2, 3))

    def test_baseline_runner_cli_supports_knn_rows(self) -> None:
        completed = subprocess.run(
            [
                PYTHON,
                "-m",
                "rtdsl.baseline_runner",
                "knn_rows",
                "--dataset",
                "authored_knn_rows_minimal",
                "--backend",
                "cpu",
            ],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["workload"], "knn_rows")
        self.assertEqual(tuple(row["neighbor_rank"] for row in payload["cpu_rows"][:3]), (1, 2, 3))

    def test_run_cpu_matches_python_reference_on_out_of_order_queries(self) -> None:
        case = {
            "query_points": (
                rt.Point(id=20, x=3.0, y=0.0),
                rt.Point(id=10, x=0.0, y=0.0),
            ),
            "search_points": (
                rt.Point(id=1, x=0.0, y=0.0),
                rt.Point(id=2, x=0.4, y=0.0),
                rt.Point(id=3, x=3.0, y=0.0),
            ),
        }
        native_rows = rt.run_cpu(knn_rows_reference, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
        self.assertEqual(native_rows, python_rows)
        self.assertEqual(tuple(row["query_id"] for row in native_rows), (10, 10, 10, 20, 20, 20))


if __name__ == "__main__":
    unittest.main()
