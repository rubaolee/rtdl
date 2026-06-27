from __future__ import annotations

import ast
import py_compile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"


class V3PhoenixRayJoinPreparedExecutionRunnerWiringTest(unittest.TestCase):
    def test_app_wires_point_location_topology_stream_to_productized_runner(self) -> None:
        source = APP.read_text(encoding="utf-8")

        for phrase in (
            "class PreparedExecutionRayJoinPointLocationTopologyStream",
            "def run_rayjoin_prepared_execution_point_location_topology_stream_workload",
            "run_point_location_topology_stream_prepared_session",
            "prepared_execution_runner_point_location_topology_stream",
            '"prepared_execution_session_runner"',
            '"prepared_execution_point_location_topology_stream"',
            '"--point-order-mode"',
            "point_order_mode=args.point_order_mode",
            "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor",
            "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
        ):
            self.assertIn(phrase, source)
        self.assertIn("point_order_mode=point_order_mode if workload == \"pip\" else \"natural\"", source)
        self.assertIn("return self._shape_count", source)

        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"broad_v3_faster_than_v2_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_claim_authorized": False', source)
        self.assertIn('"v4_embedding_or_external_zero_copy_authorized": False', source)
        self.assertIn('"full_all_app_rerun_authorized_by_this_packet"] = False', source)
        self.assertNotIn('"public_speedup_claim_authorized": True', source)
        self.assertNotIn('"rtdl_beats_rayjoin_claim_authorized": True', source)
        self.assertNotIn('"true_zero_copy_claim_authorized": True', source)

    def test_runtime_helper_is_generic_not_rayjoin_named(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("def run_point_location_topology_stream_prepared_session", source)
        self.assertIn('primitive="point_location_topology_stream"', source)
        self.assertIn('"run_point_location_topology_stream_prepared_session"', source)
        helper_start = source.index("def run_point_location_topology_stream_prepared_session")
        helper_end = source.index("def describe_prepared_execution_user_pattern", helper_start)
        helper_body = source[helper_start:helper_end]
        self.assertNotIn("rayjoin", helper_body.lower())
        self.assertIn("external_device_buffer_interop_authorized", helper_body)
        self.assertIn("focused_material_gain_required_before_all_app", helper_body)
        self.assertIn("full_all_app_rerun_authorized_by_this_packet", helper_body)

    def test_shape_pair_active_count_does_not_receive_pip_point_ordering(self) -> None:
        source = APP.read_text(encoding="utf-8")
        tree = ast.parse(source)

        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_rayjoin_prepared_optix_shape_pair_active_count_workload"
        ]

        self.assertGreaterEqual(len(calls), 2)
        for call in calls:
            keyword_names = {keyword.arg for keyword in call.keywords}
            self.assertNotIn("point_order_mode", keyword_names)

        self.assertIn('args.execution_route == "prepared_optix_shape_pair_active_count"', source)
        self.assertIn('args.point_order_mode != "natural"', source)
        self.assertIn("--point-order-mode is only valid for PIP point-location routes", source)

    def test_modified_python_files_compile(self) -> None:
        py_compile.compile(str(APP), doraise=True)
        py_compile.compile(str(PREPARED_EXECUTION), doraise=True)


if __name__ == "__main__":
    unittest.main()
