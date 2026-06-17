from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4493M97TriangleLocalHashUniquePrototypeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["dataset"]: row for row in cls.packet["rows"]}

    def test_packet_validates_local_hash_prototype(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.triangle_local_hash_unique_prototype.goal4493.v1",
            self.packet["version"],
        )
        self.assertEqual(3, self.packet["case_count"])
        self.assertEqual(3, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(self.packet["summary"]["all_validated"])
        self.assertTrue(JSONL.exists())
        self.assertIn("cuda_12.4", self.packet["ptxas_version"])
        self.assertEqual(20_000_000, self.packet["parameters"]["target_two_hop_rows"])
        self.assertEqual(2048, self.packet["parameters"]["local_hash_bound"])
        self.assertEqual(4096, self.packet["parameters"]["local_hash_capacity"])

        for dataset, row in self.rows.items():
            self.assertTrue(row["validation_ok"], dataset)
            self.assertEqual(0, row["overflow_total"], dataset)
            self.assertGreaterEqual(row["selected_two_hop_rows"], 20_000_000)
            self.assertEqual(row["local_unique_total"], row["reference_unique_total"])

        self.assertGreater(self.rows["com_lj"]["local_hash_speedup_vs_reference"], 1.05)
        self.assertGreater(self.rows["soc_livejournal1"]["local_hash_speedup_vs_reference"], 0.95)
        self.assertGreater(self.rows["com_orkut"]["local_hash_speedup_vs_reference"], 1.25)

    def test_claim_boundary_keeps_route_unpromoted(self) -> None:
        boundary = self.packet["claim_boundary"]

        self.assertTrue(boundary["prototype_only"])
        self.assertTrue(boundary["selected_small_source_groups_only"])
        self.assertFalse(boundary["route_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        for row in self.rows.values():
            row_boundary = row["prototype_boundary"]
            self.assertFalse(row_boundary["hybrid_large_tail_fallback_implemented"])
            self.assertFalse(row_boundary["route_changed"])

    def test_report_index_and_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("triangle_counting")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4493", report)
        self.assertIn("local-hash", report)
        self.assertIn("large-tail fallback", report)
        self.assertIn("Goal4493 Triangle local-hash unique prototype", index)
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4505.v1",
            route["version"],
        )
        self.assertIn("Goal4493", route["evidence_refs"])
        self.assertIn("Goal4494", route["next_runtime_action"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4505.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4493", adequacy["evidence_refs"])
        self.assertIn("Goal4494", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
