from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.jsonl"
RAW_DIR = ROOT / "docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17"
REPORT = ROOT / "docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"


class Goal4494M98TriangleLocalHashIntegratedCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.comparisons = cls.packet["summary"]["comparisons"]
        cls.rows = {(row["dataset"], row["builder"]): row for row in cls.packet["rows"]}

    def test_packet_rejects_integrated_local_hash_candidate(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.triangle_local_hash_integrated_candidate.goal4494.v1",
            self.packet["version"],
        )
        self.assertEqual(6, self.packet["case_count"])
        self.assertEqual(6, self.packet["ok_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(RAW_DIR.exists())
        self.assertTrue(self.packet["summary"]["all_counts_match"])
        self.assertEqual(
            ["numba_direct_sort_rle", "numba_direct_sort_rle_local_hash_2048"],
            self.packet["parameters"]["builders"],
        )
        self.assertEqual(15_000_000, self.packet["parameters"]["segment_max_two_hop_rows"])
        self.assertEqual(2_000_000, self.packet["parameters"]["scene_max_directed_edges"])

        for dataset, comparison in self.comparisons.items():
            self.assertTrue(comparison["count_matches"], dataset)
            self.assertEqual("reject_hybrid_candidate", comparison["decision"], dataset)
            self.assertLess(comparison["baseline_over_hybrid_backend"], 1.0, dataset)
            self.assertLess(comparison["baseline_over_hybrid_segment_ray_build"], 1.0, dataset)

        self.assertLess(self.comparisons["soc_livejournal1"]["baseline_over_hybrid_backend"], 0.40)
        self.assertLess(self.comparisons["soc_livejournal1"]["baseline_over_hybrid_segment_ray_build"], 0.20)

    def test_raw_rows_match_expected_counts_and_boundaries(self) -> None:
        expected_counts = {
            "com_lj": 177_820_130,
            "soc_livejournal1": 285_730_264,
            "com_orkut": 627_584_181,
        }
        for dataset, expected in expected_counts.items():
            for builder in ("numba_direct_sort_rle", "numba_direct_sort_rle_local_hash_2048"):
                row = self.rows[(dataset, builder)]
                self.assertEqual("ok", row["status"], (dataset, builder))
                self.assertEqual(expected, row["observed_triangle_count"], (dataset, builder))
                self.assertTrue(row["count_matches_expected"], (dataset, builder))
                self.assertTrue((ROOT / row["raw_payload_file"]).exists(), (dataset, builder))
                self.assertFalse(row["claim_boundary"]["route_changed"], (dataset, builder))
                self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"], (dataset, builder))
                self.assertFalse(row["claim_boundary"]["native_engine_customization"], (dataset, builder))
                self.assertFalse(row["claim_boundary"]["app_specific_native_engine_callback"], (dataset, builder))

    def test_report_index_guidance_and_app_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        app_source = APP.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("triangle_counting")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4494", report)
        self.assertIn("reject", report)
        self.assertIn("per-segment local-hash", report)
        self.assertIn("Goal4494 Triangle integrated local-hash candidate", index)
        self.assertIn("numba_direct_sort_rle_local_hash_2048", app_source)
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4501.v1",
            route["version"],
        )
        self.assertIn("Goal4494", route["evidence_refs"])
        self.assertIn("per-segment local-hash", " ".join(route["rejected_or_unpromoted_candidates"]))
        self.assertIn("Keep `numba_direct_sort_rle`", route["next_runtime_action"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4501.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4494", adequacy["evidence_refs"])
        self.assertIn("Keep `numba_direct_sort_rle`", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
