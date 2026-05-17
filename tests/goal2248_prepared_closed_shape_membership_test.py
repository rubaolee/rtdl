from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
RUNNER = ROOT / "scripts" / "goal2192_rayjoin_same_query_stream_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2248_prepared_closed_shape_membership_2026-05-17.md"


class Goal2248PreparedClosedShapeMembershipTest(unittest.TestCase):
    def test_native_prepared_symbols_are_generic(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        for symbol in (
            "rtdl_optix_prepare_point_closed_shape_membership_2d",
            "rtdl_optix_run_prepared_point_closed_shape_membership_2d",
            "rtdl_optix_destroy_prepared_point_closed_shape_membership_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", workloads)
        self.assertIn("run_prepared_point_closed_shape_membership_2d_optix", workloads)

    def test_python_public_surface_and_runner_use_prepared_path(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("class PreparedOptixPointClosedShapeMembership2D", runtime)
        self.assertIn("def prepare_point_closed_shape_membership_2d_optix", runtime)
        self.assertIn("PreparedOptixPointClosedShapeMembership2D", init)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", init)
        self.assertIn("prepared_closed_shape_membership", runner)
        self.assertIn('"implementation_path": "prepared_closed_shape_membership_2d_optix"', runner)

    def test_report_keeps_claim_boundary_before_pod_timing(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2248", text)
        self.assertIn("prepared generic closed-shape membership", text)
        self.assertIn("pod timing recorded by Goal2249", text)
        self.assertIn("the measured performance claim lives in the Goal2249", text)
        self.assertIn("RayJoin/PIP/polygon naming remains in the Python application", text)


if __name__ == "__main__":
    unittest.main()
