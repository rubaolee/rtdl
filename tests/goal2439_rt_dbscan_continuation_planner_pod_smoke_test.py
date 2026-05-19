from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2439_rt_dbscan_continuation_planner_pod_smoke"
REPORT = ROOT / "docs" / "reports" / "goal2439_rt_dbscan_continuation_planner_pod_smoke_2026-05-19.md"


class Goal2439RtDbscanContinuationPlannerPodSmokeTest(unittest.TestCase):
    def test_summary_records_both_planner_branches_and_boundaries(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in summary["rows"]}

        self.assertEqual(summary["commit"], "1aa52fad5746899c768fa8e4473bca59344569e7")
        self.assertFalse(summary["claim_boundary"]["hidden_dispatcher"])
        self.assertFalse(summary["claim_boundary"]["release_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

        self.assertEqual(rows["tiny_validated"]["selected_mode"], "cpu_reference")
        self.assertTrue(rows["tiny_validated"]["matches_reference"])
        self.assertTrue(rows["tiny_validated"]["not_hidden_dispatcher"])

        full = rows["clustered4096_full_adjacency_validated"]
        self.assertEqual(full["selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertTrue(full["matches_reference"])
        self.assertTrue(full["full_stream_fits_budget"])
        self.assertTrue(full["rt_core_accelerated"])

        chunked = rows["clustered32768_chunked_adjacency_no_validation"]
        self.assertEqual(chunked["selected_mode"], "optix_rt_core_chunked_adjacency_cupy_components_3d")
        self.assertIsNone(chunked["matches_reference"])
        self.assertFalse(chunked["full_stream_fits_budget"])
        self.assertTrue(chunked["rt_core_accelerated"])

    def test_artifacts_expose_plan_metadata(self) -> None:
        for name in (
            "tiny_validated.json",
            "clustered4096_full_adjacency_validated.json",
            "clustered32768_chunked_adjacency_no_validation.json",
        ):
            with self.subTest(name=name):
                payload = json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
                plan = payload["metadata"]["execution_plan"]
                self.assertEqual(plan["adapter"], "plan_rt_dbscan_continuation_execution")
                self.assertEqual(plan["planner_surface"], "benchmark_app_plan_explain_not_engine_dispatch")
                self.assertEqual(plan["evidence_goals"], ["Goal2431", "Goal2433", "Goal2435"])
                self.assertTrue(plan["not_hidden_dispatcher"])
                self.assertFalse(plan["release_claim_authorized"])
                self.assertFalse(plan["paper_reproduction_claim_authorized"])
                self.assertEqual(payload["selected_mode"], plan["selected_mode"])
                self.assertEqual(payload["pod_smoke"]["source_commit"], "1aa52fad5746899c768fa8e4473bca59344569e7")

    def test_chunked_artifact_keeps_single_pass_chunk_metadata(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "clustered32768_chunked_adjacency_no_validation.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["metadata"]["adjacency_write_pass_count"], 1)
        self.assertEqual(payload["metadata"]["chunk_count"], 8)
        self.assertGreater(payload["metadata"]["total_directed_edge_count"], 100_000_000)
        self.assertLess(
            payload["metadata"]["max_chunk_directed_edge_count"],
            payload["metadata"]["total_directed_edge_count"],
        )
        self.assertTrue(payload["metadata"]["materializes_bounded_directed_adjacency_chunks"])

    def test_report_preserves_smoke_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod-smoked, with boundary", report)
        self.assertIn("not a new performance claim", report)
        self.assertIn("does not add native DBSCAN ABI", report)
        self.assertIn("does not authorize a broad RT-core speedup", report)
        self.assertIn("not run", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
