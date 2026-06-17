from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4476_v3_0_m80_triangle_weight_sum_sync_negative_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4476_v3_0_m80_triangle_weight_sum_sync_negative_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4476V30M80TriangleWeightSumSyncNegativePacketTest(unittest.TestCase):
    def test_packet_records_negative_reverted_result(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4476, packet["goal"])
        self.assertEqual("negative_result_reverted", packet["status"])
        self.assertFalse(packet["claim_boundary"]["optimization_promoted"])
        self.assertFalse(packet["claim_boundary"]["current_best_route_changed"])
        self.assertGreater(rows["com_lj"]["m80_no_sync_total_slower_than_m78"], 1.7)
        self.assertGreater(rows["soc_livejournal1"]["m80_explicit_sync_backend_slower_than_m78"], 1.2)
        self.assertGreater(rows["com_orkut"]["m80_no_sync_backend_slower_than_m78"], 1.0)
        self.assertIn("M78 remains", packet["interpretation"]["current_best_route"])

    def test_report_and_registry_block_promotion(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("negative-result packet", report)
        self.assertIn("Both implementation commits were reverted", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4484.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4484.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4476", route["evidence_refs"])
        self.assertIn("Goal4476", triangle["evidence_refs"])
        self.assertIn("weight-sum telemetry", route["next_runtime_action"])
        self.assertIn("partner materialization", triangle["next_generic_runtime_action"])
        self.assertIn("segment-ray construction", triangle["next_generic_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(triangle["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
