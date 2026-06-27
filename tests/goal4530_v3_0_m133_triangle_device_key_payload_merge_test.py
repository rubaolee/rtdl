from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4530_v3_0_m133_triangle_device_key_payload_merge_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4530_v3_0_m133_triangle_device_key_payload_merge_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/triangle_counting/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4530_m133_triangle_device_key_payload_merge.py"
SOURCE = ROOT / "src/rtdsl/v3_0_prepared_graph_chunk_executor.py"
INIT = ROOT / "src/rtdsl/__init__.py"


class Goal4530V30M133TriangleDeviceKeyPayloadMergeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_device_merge_validates_cross_chunk_duplicates(self) -> None:
        packet = self.packet
        merge = packet["device_merge"]
        self.assertEqual(
            "rtdl.v3_0.triangle_device_key_payload_merge.goal4530.v1",
            packet["version"],
        )
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertTrue(packet["runtime"]["runtime_executed"])
        self.assertEqual("cupy", packet["runtime"]["partner"])
        self.assertEqual([11, 17, 23, 29, 31, 37], merge["unique_keys"])
        self.assertEqual([6, 5, 5, 1, 1, 1], merge["counts"])
        self.assertEqual(19, merge["total_weight"])
        self.assertEqual(3, merge["cross_chunk_duplicate_delta"])
        self.assertFalse(merge["host_key_materialization_before_merge"])
        self.assertFalse(merge["host_count_materialization_before_merge"])
        self.assertEqual(merge["unique_keys"], packet["host_reference"]["unique_keys"])
        self.assertEqual(merge["counts"], packet["host_reference"]["counts"])

    def test_m113_gate_now_only_blocks_on_graph_capture(self) -> None:
        current = self.packet["validation"]["current_triangle_readiness"]
        future = self.packet["validation"]["future_generic_payload_readiness"]
        boundary = self.packet["claim_boundary"]

        self.assertFalse(current["ready_for_m113_plan"])
        self.assertEqual(("prepared_graph_capture_not_validated",), tuple(current["blockers"]))
        self.assertTrue(future["ready_for_m113_plan"])
        self.assertTrue(boundary["device_key_payload_merge_validated"])
        self.assertFalse(boundary["prepared_graph_capture_validated"])
        self.assertFalse(boundary["m113_promotion_authorized_for_current_triangle"])
        self.assertFalse(boundary["app_specific_native_callback_required"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])

    def test_docs_source_and_exports_reference_m133(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        self.assertIn("Goal4530 / V3 M133", report)
        self.assertIn("Current blockers: `prepared_graph_capture_not_validated`", report)
        self.assertIn("Goal4530", readme)
        self.assertIn("Goal4530 Triangle device key-payload merge", index)
        self.assertIn("combine_v3_chunked_unique_count_key_payloads_cupy", script)
        self.assertIn("device_associative_unique_count_key_payload_merge", source)
        self.assertIn("combine_v3_chunked_unique_count_key_payloads_cupy", init)
        self.assertTrue(hasattr(rt, "combine_v3_chunked_unique_count_key_payloads_cupy"))


if __name__ == "__main__":
    unittest.main()
