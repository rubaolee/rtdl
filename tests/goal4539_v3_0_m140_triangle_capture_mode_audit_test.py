from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4539_m140_triangle_capture_mode_audit.py"


class Goal4539V30M140TriangleCaptureModeAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_capture_mode_matrix_rejects_graph_capture_after_valid_stream_launch(self) -> None:
        packet = self.packet
        runtime = packet["runtime"]
        self.assertEqual("rtdl.v3_0.triangle_capture_mode_audit.goal4539.v1", packet["version"])
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertTrue(runtime["runtime_executed"])
        self.assertEqual(20, runtime["expected_weighted_sum"])
        self.assertEqual(20, runtime["device_output_stream_prelaunch_weighted_sum"])
        self.assertTrue(runtime["device_output_stream_prelaunch_validated"])
        self.assertEqual([], list(runtime["graph_capture_validated_modes"]))
        self.assertTrue(runtime["graph_capture_mode_independent_reject"])

    def test_all_capture_modes_fail_closed_without_claim_promotion(self) -> None:
        rows = {row["mode"]: row for row in self.packet["runtime"]["capture_modes"]}
        self.assertEqual({"default", "relaxed", "global", "thread_local"}, set(rows))
        for row in rows.values():
            self.assertEqual("reject_error", row["capture_status"], row["mode"])
            self.assertIsNone(row["replay_weighted_sum"], row["mode"])
            self.assertIn("OptiX error: CUDA error", row["error"])
        boundary = self.packet["claim_boundary"]
        self.assertTrue(boundary["prepared_weighted_replay_device_output_stream_validated"])
        self.assertFalse(boundary["prepared_weighted_replay_graph_capture_validated"])
        self.assertFalse(boundary["m113_promotion_authorized_for_future_triangle_shape"])
        self.assertFalse(boundary["queue_reclassification_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])

    def test_non_graph_acceptance_is_evidence_only(self) -> None:
        acceptance = self.packet["acceptance"]
        self.assertTrue(acceptance["non_graph_stream_continuation_evidence_accepted"])
        self.assertTrue(acceptance["m113_graph_capture_still_blocked"])
        self.assertFalse(acceptance["queue_reclassification_done"])
        self.assertIn("DEVICE_OUTPUT_STREAM_CONTINUATION", acceptance["non_graph_stream_continuation_contract"])

    def test_report_index_and_script_capture_goal4539(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Goal4539 / V3 M140", report)
        self.assertIn("Graph capture mode-independent reject: `True`", report)
        self.assertIn("Queue reclassification done: `False`", report)
        self.assertIn("Goal4539 Triangle capture-mode audit", index)
        self.assertIn("streamCaptureModeRelaxed", script)
        self.assertIn("streamCaptureModeThreadLocal", script)


if __name__ == "__main__":
    unittest.main()
