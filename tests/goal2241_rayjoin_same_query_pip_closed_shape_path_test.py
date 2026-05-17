from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2192_rayjoin_same_query_stream_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md"


class Goal2241RayjoinSameQueryPipClosedShapePathTest(unittest.TestCase):
    def test_runner_routes_pip_optix_through_closed_shape_membership(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("def _run_pip_optix_closed_shape", text)
        self.assertIn("def _prepare_backend_inputs", text)
        self.assertIn("rt.closed_shape_membership_2d_optix", text)
        self.assertIn("rt.prepare_point_closed_shape_membership_2d_optix", text)
        self.assertIn('"implementation_path": "prepared_closed_shape_membership_2d_optix"', text)
        self.assertIn('"uses_generic_closed_shape_membership": workload == "pip" and backend == "optix"', text)
        self.assertIn('"input_preparation_path": "prepared_shape_scene_and_prepacked_points_once_per_run_stream"', text)

    def test_runner_preserves_rayjoin_row_contract_in_python(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn('"polygon_id": int(row["shape_id"])', text)
        self.assertIn('"contains": int(row["membership"])', text)
        self.assertIn('result_mode="positive_hits"', text)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2241", text)
        self.assertIn("native surface app-agnostic", text)
        self.assertIn("This mapping is deliberately in Python", text)
        self.assertIn("packs the PIP points and shapes once", text)
        self.assertIn("not a full RayJoin reproduction", text)


if __name__ == "__main__":
    unittest.main()
