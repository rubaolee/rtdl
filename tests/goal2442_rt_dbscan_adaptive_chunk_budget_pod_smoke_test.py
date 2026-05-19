from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke"
REPORT = ROOT / "docs" / "reports" / "goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke_2026-05-19.md"


class Goal2442RtDbscanAdaptiveChunkBudgetPodSmokeTest(unittest.TestCase):
    def test_summary_proves_degree_budget_chunk_split(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        row = summary["row"]

        self.assertEqual(summary["commit"], "931275f6846b2e6ba19f336e814089783584d4d7")
        self.assertEqual(row["mode"], "optix_rt_core_chunked_adjacency_cupy_components_3d")
        self.assertEqual(row["point_count"], 32768)
        self.assertEqual(row["max_directed_edges_per_chunk"], 8_000_000)
        self.assertEqual(row["chunk_planning_policy"], "adaptive_degree_budget_and_max_point_count")
        self.assertEqual(row["count_chunk_count"], 8)
        self.assertEqual(row["chunk_count"], 18)
        self.assertLessEqual(row["max_chunk_directed_edge_count"], row["max_directed_edges_per_chunk"])
        self.assertGreater(row["total_directed_edge_count"], 100_000_000)
        self.assertEqual(row["adjacency_write_pass_count"], 1)
        self.assertTrue(row["rt_core_accelerated"])

        self.assertFalse(summary["claim_boundary"]["release_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

    def test_full_artifact_preserves_runtime_metadata(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "clustered32768_chunk_budget_8000000.json").read_text(encoding="utf-8"))
        metadata = payload["metadata"]

        self.assertEqual(metadata["max_directed_edges_per_chunk"], 8_000_000)
        self.assertEqual(metadata["chunk_planning_policy"], "adaptive_degree_budget_and_max_point_count")
        self.assertEqual(metadata["chunk_count"], len(metadata["chunk_directed_edge_counts"]))
        self.assertEqual(max(metadata["chunk_directed_edge_counts"]), metadata["max_chunk_directed_edge_count"])
        self.assertLessEqual(metadata["max_chunk_directed_edge_count"], 8_000_000)
        self.assertTrue(metadata["materializes_bounded_directed_adjacency_chunks"])
        self.assertFalse(payload["claim_boundary"]["paper_speedup_claim_authorized"])

    def test_report_keeps_boundary_explicit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod-smoked, with boundary", report)
        self.assertIn("memory-control result, not a speedup result", report)
        self.assertIn("7,999,889 <= 8,000,000", report)
        self.assertIn("does not add native DBSCAN ABI", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
