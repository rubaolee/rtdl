from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/rt_dbscan/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4528_m132_rtdbscan_prepared_graph_capture.py"
SOURCE = ROOT / "src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py"
INIT = ROOT / "src/rtdsl/__init__.py"


class Goal4528V30M132RtDbscanPreparedGraphCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_runtime_packet_validates_prepared_graph_capture(self) -> None:
        packet = self.packet

        self.assertEqual("rtdl.v3_0.rtdbscan_prepared_graph_capture.goal4528.v1", packet["version"])
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertTrue(packet["runtime"]["runtime_executed"])
        self.assertEqual("cupy", packet["runtime"]["partner"])
        self.assertEqual(2, packet["runtime"]["chunk_count"])
        self.assertTrue(packet["readiness"]["api_shape_ready"])
        self.assertTrue(packet["readiness"]["live_chunk_handle_smoke_validated"])
        self.assertTrue(packet["readiness"]["prepared_graph_capture_validated"])
        self.assertTrue(packet["readiness"]["ready_for_m113_plan"])
        self.assertEqual(31, packet["validation"]["readiness"]["chunk_count"])
        self.assertEqual((), tuple(packet["validation"]["readiness"]["blockers"]))

    def test_chunks_capture_and_replay_without_materialization(self) -> None:
        chunks = self.packet["chunks"]

        self.assertEqual([0, 6], [chunk["start"] for chunk in chunks])
        self.assertEqual([0, 48], [chunk["x_device_pointer_offset_bytes"] for chunk in chunks])
        for chunk in chunks:
            self.assertEqual(6, chunk["point_count"])
            self.assertTrue(chunk["graph_capture"]["cuda_graph_captured"])
            self.assertEqual(1, chunk["graph_capture"]["fixed_iteration_count"])
            self.assertEqual(
                "fixed_iteration_count_no_host_d2h_inside_capture",
                chunk["graph_capture"]["capture_mode"],
            )
            self.assertTrue(chunk["graph_matches_normal_fixed_iteration"])
            self.assertTrue(chunk["point_coordinate_upload_avoided"])
            self.assertTrue(chunk["point_coordinate_host_intermediate_tuple_avoided"])
            self.assertEqual("caller_owned_cupy_device_columns", chunk["point_coordinate_columns_source"])
            self.assertTrue(chunk["pair_materialization_avoided"])
            self.assertFalse(chunk["graph_capture"]["host_materialization_before_partner"])
            self.assertFalse(chunk["graph_capture"]["native_abi_added"])
            for replay in chunk["graph_replays"]:
                self.assertTrue(replay["cuda_graph_replay"])
                self.assertEqual([0, 3, 0, 0], replay["label_counts"])
                self.assertEqual(3, replay["flag_true_count"])
                self.assertEqual(3, replay["negative_label_count"])

    def test_report_docs_exports_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertIn("Goal4528 / V3 M132", report)
        self.assertIn("Ready for M113 plan: `True`", report)
        self.assertIn("Goal4528", readme)
        self.assertIn("Goal4528 RT-DBSCAN prepared graph capture", index)
        self.assertIn("prepare_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_graph_preview_3d", script)
        self.assertIn("fixed_iteration_count_no_host_d2h_inside_capture", source)
        self.assertTrue(hasattr(rt, "prepare_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_graph_preview_3d"))
        self.assertIn("V28CapturedFixedRadiusPartitionConvergencePredicateDirectStatusGraphCupyPreview3D", init)
        self.assertFalse(boundary["current_route_changed"])
        self.assertTrue(boundary["m113_promotion_authorized"])
        self.assertTrue(boundary["prepared_graph_capture_validated"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
