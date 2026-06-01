from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2962_large_scale_v2_5_stress_probe_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2962_large_scale_stress_pod"
RTNN = ARTIFACT_DIR / "goal2962_rtnn_262k.json"
HAUSDORFF = ARTIFACT_DIR / "goal2962_hausdorff_16k.json"
DBSCAN = ARTIFACT_DIR / "goal2962_rt_dbscan_262k.json"
EXPECTED_COMMIT = "8deb21bea3930830ad03d3d7410356c786af5479"


class Goal2962LargeScaleV25StressProbeTest(unittest.TestCase):
    def test_rtnn_262k_uses_four_graph_chunks_and_beats_same_contract_cupy(self) -> None:
        payload = json.loads(RTNN.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual(262144, payload["point_count"])
        self.assertEqual(65536, payload["query_batch_size"])
        for row in payload["rows"]:
            with self.subTest(distribution=row["distribution"]):
                self.assertEqual(4, row["rtdl_phase_summary"]["batch_count"])
                self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                self.assertGreater(float(row["cupy_grid_over_rtdl_elapsed_ratio"]), 2.0)
                self.assertEqual(0.0, float(row["rtdl_phase_summary"]["upload_sec"]))
                self.assertFalse(row["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_hausdorff_16k_exact_rt_path_matches_cupy_baseline(self) -> None:
        payload = json.loads(HAUSDORFF.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual(16384, payload["scenario"]["points_a"])
        self.assertEqual(16384, payload["scenario"]["points_b"])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertEqual(0.0, float(payload["distance_error"]))
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])
        self.assertLess(float(payload["rtdl_over_cupy_grid_elapsed_ratio"]), 1.0)
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_xhd_claim_authorized"])

    def test_rt_dbscan_262k_grouped_stream_stays_rt_accelerated_and_compact(self) -> None:
        payload = json.loads(DBSCAN.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual([262144], payload["point_counts"])
        self.assertTrue(payload["signatures_match"])
        self.assertTrue(payload["grouped_stream_rt_core_accelerated"])
        self.assertTrue(payload["grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream"])
        self.assertGreater(float(payload["min_grouped_stream_speedup_vs_prepared_cupy_grid"]), 4.0)
        self.assertFalse(payload["claim_boundary"]["paper_speedup_claim_authorized"])

    def test_report_and_readiness_preserve_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for phrase in (
            "Goal2962",
            "262,144",
            "`3.359x`",
            "`0.937x`",
            "`4.580x`",
            "does not authorize",
        ):
            self.assertIn(phrase, text)
        self.assertIn(
            "docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md",
            packet["required_reports"],
        )
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
