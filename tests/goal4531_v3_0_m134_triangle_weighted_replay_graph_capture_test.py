from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/triangle_counting/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4531_m134_triangle_weighted_replay_graph_capture.py"
PY_SOURCE = ROOT / "src/rtdsl/optix_runtime.py"
NATIVE_SOURCE = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
INIT = ROOT / "src/rtdsl/__init__.py"


class Goal4531V30M134TriangleWeightedReplayGraphCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_weighted_replay_device_output_stream_validates_and_graph_capture_fail_closes(self) -> None:
        packet = self.packet
        runtime = packet["runtime"]
        self.assertEqual(
            "rtdl.v3_0.triangle_weighted_replay_graph_capture.goal4531.v1",
            packet["version"],
        )
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertTrue(runtime["runtime_executed"])
        self.assertEqual("optix", runtime["backend"])
        self.assertEqual("cupy", runtime["partner"])
        self.assertEqual(20, runtime["expected_weighted_sum"])
        self.assertEqual(20, runtime["normal_host_scalar_weighted_sum"])
        self.assertEqual(20, runtime["device_output_stream_weighted_sum"])
        self.assertTrue(runtime["device_output_stream_validated"])
        self.assertFalse(runtime["graph_capture_validated"])
        self.assertEqual([], runtime["graph_replay_weighted_sums"])
        self.assertIn("OptiX error: CUDA error", runtime["graph_capture_error"])
        self.assertEqual("reject_fail_closed", packet["validation"]["graph_capture_status"])

    def test_triangle_m113_gate_stays_blocked_and_current_route_stays_scoped(self) -> None:
        readiness = self.packet["validation"]["readiness"]
        boundary = self.packet["claim_boundary"]
        self.assertFalse(readiness["ready_for_m113_plan"])
        self.assertEqual(("prepared_graph_capture_not_validated",), tuple(readiness["blockers"]))
        self.assertEqual(0, readiness["chunk_count"])
        self.assertTrue(boundary["prepared_weighted_replay_device_output_stream_validated"])
        self.assertFalse(boundary["prepared_weighted_replay_graph_capture_validated"])
        self.assertFalse(boundary["m113_promotion_authorized_for_future_triangle_shape"])
        self.assertFalse(boundary["m113_replaces_current_triangle_route"])
        self.assertFalse(boundary["app_specific_native_callback_required"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])

    def test_docs_source_and_exports_reference_m134(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        py_source = PY_SOURCE.read_text(encoding="utf-8")
        native_source = NATIVE_SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        self.assertIn("Goal4531 / V3 M134", report)
        self.assertIn("Device-output stream validated: `True`", report)
        self.assertIn("Graph capture validated: `False`", report)
        self.assertIn("Goal4531", readme)
        self.assertIn("Goal4531 Triangle weighted replay graph capture", index)
        self.assertIn("prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor", script)
        self.assertIn("PreparedOptixRayBatchWeightedSumDeviceOutputGraphExecutor3D", py_source)
        self.assertIn("NativeRayBatchWeightedSumDeviceOutputGraphExecutor", native_source)
        self.assertIn("PreparedOptixRayBatchWeightedSumDeviceOutputGraphExecutor3D", init)
        self.assertTrue(
            hasattr(rt, "PreparedOptixRayBatchWeightedSumDeviceOutputGraphExecutor3D")
        )


if __name__ == "__main__":
    unittest.main()
