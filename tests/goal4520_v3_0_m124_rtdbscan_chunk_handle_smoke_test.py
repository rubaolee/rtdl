from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/rt_dbscan/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4520_m124_rtdbscan_chunk_handle_smoke.py"


class Goal4520V30M124RtDbscanChunkHandleSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_runtime_packet_validates_live_chunk_handle_smoke_only(self) -> None:
        packet = self.packet
        self.assertEqual("rtdl.v3_0.rtdbscan_chunk_handle_smoke.goal4520.v1", packet["version"])
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertTrue(packet["runtime"]["runtime_executed"])
        self.assertEqual("cupy", packet["runtime"]["partner"])
        self.assertEqual(2, packet["runtime"]["chunk_count"])
        self.assertTrue(packet["readiness"]["api_shape_ready"])
        self.assertTrue(packet["readiness"]["live_chunk_handle_smoke_validated"])
        self.assertFalse(packet["readiness"]["prepared_graph_capture_validated"])
        self.assertFalse(packet["readiness"]["ready_for_m113_plan"])
        self.assertEqual(
            ["prepared_graph_capture_not_validated"],
            packet["validation"]["readiness"]["blockers"],
        )

    def test_chunks_reuse_caller_owned_slices_without_pair_rows_or_native_abi(self) -> None:
        chunks = self.packet["chunks"]
        self.assertEqual([0, 6], [chunk["start"] for chunk in chunks])
        self.assertEqual([0, 48], [chunk["x_device_pointer_offset_bytes"] for chunk in chunks])
        for chunk in chunks:
            self.assertEqual(6, chunk["point_count"])
            self.assertEqual(2, chunk["component_signature_runs"])
            self.assertTrue(chunk["closed_after_smoke"])
            self.assertTrue(chunk["point_coordinate_upload_avoided"])
            self.assertTrue(chunk["point_coordinate_host_intermediate_tuple_avoided"])
            self.assertEqual("caller_owned_cupy_device_columns", chunk["point_coordinate_columns_source"])
            self.assertTrue(chunk["pair_materialization_avoided"])
            self.assertFalse(chunk["native_abi_added"])
            self.assertEqual(
                chunk["expected_x_device_pointer_offset_bytes"],
                chunk["x_device_pointer_offset_bytes"],
            )
            for index, row in enumerate(chunk["repeat_rows"], start=1):
                self.assertEqual("accept", row["metadata_status"])
                self.assertTrue(row["handle_reused"])
                self.assertEqual(index, row["run_index"])
                self.assertEqual([3], row["label_counts_nonzero"])
                self.assertEqual(3, row["flag_true_count"])
                self.assertEqual(3, row["negative_label_count"])

    def test_report_docs_and_script_keep_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertIn("Goal4520 / V3 M124", report)
        self.assertIn("Live chunk-handle smoke validated: `True`", report)
        self.assertIn("prepared graph capture", report)
        self.assertIn("Goal4520", readme)
        self.assertIn("Goal4520 RT-DBSCAN chunk-handle smoke", index)
        self.assertIn(
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d",
            script,
        )
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["m113_promotion_authorized"])
        self.assertFalse(boundary["prepared_graph_capture_validated"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
