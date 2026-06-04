from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal3312_prepared_point_batch_graph_negative_probe_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3312_batch_graph_replay_negative_probe_2026-06-04.json"


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
        self.assertIn("cuGraphGetNodes", body)
        self.assertIn("expected OptiX launch nodes", body)
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
        self.assertIn("validate_on_prepare: bool = True", runtime)
        self.assertIn("graph replay failed validation", runtime)
        self.assertIn("validated_on_prepare", runtime)
        self.assertIn("prepared_points_device_filtered_batch_graph_replay", runtime)
        self.assertIn("if mode_value == 10", runtime)
        self.assertIn('"true_zero_copy_claim_authorized": False', runtime)
        self.assertIn("PreparedOptixPointClosedShapeBatchCountGraph2D", init_text)

    def test_report_records_negative_fail_closed_result(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("fail-closed negative probe", report)
        self.assertIn("not currently usable as a performance optimization", report)
        self.assertIn("not a performance win", report)
        self.assertEqual(artifact["graph_status"], "failed_closed")
        self.assertEqual(artifact["exact"], 2)
        self.assertEqual(artifact["single"], 2)
        self.assertEqual(artifact["batch"], [2, 2, 2, 2, 2])
        self.assertIn("failed validation", artifact["error"])
        self.assertFalse(any(artifact["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
