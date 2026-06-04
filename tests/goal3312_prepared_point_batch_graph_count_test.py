from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"


class Goal3312PreparedPointBatchGraphCountTest(unittest.TestCase):
    def test_native_graph_symbols_are_exported(self) -> None:
        symbols = (
            "rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d",
            "rtdl_optix_replay_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d",
            "rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d",
        )
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        for symbol in symbols:
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)

    def test_native_graph_handle_captures_generic_batch_count_replay(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("struct PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D")
        end = text.index(
            "static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix",
            start,
        )
        body = text[start:end]
        self.assertIn("cuStreamBeginCapture", body)
        self.assertIn("cuGraphInstantiate", body)
        self.assertIn("cuGraphLaunch", body)
        self.assertIn("cuGraphExecDestroy", body)
        self.assertIn("cuGraphDestroy", body)
        self.assertIn("reset_closed_shape_membership_phase_timings(10u)", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_python_graph_handle_is_context_managed_and_claim_bounded(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        self.assertIn("class PreparedOptixPointClosedShapeBatchCountGraph2D", runtime)
        self.assertIn("def prepare_device_filtered_prepared_points_batch_graph", runtime)
        self.assertIn("def replay(self) -> tuple[int, ...]", runtime)
        self.assertIn("prepared_points_device_filtered_batch_graph_replay", runtime)
        self.assertIn("if mode_value == 10", runtime)
        self.assertIn('"true_zero_copy_claim_authorized": False', runtime)
        self.assertIn("PreparedOptixPointClosedShapeBatchCountGraph2D", init_text)


if __name__ == "__main__":
    unittest.main()
