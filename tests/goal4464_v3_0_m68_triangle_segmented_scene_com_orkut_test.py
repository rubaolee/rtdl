from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4464_v3_0_m68_triangle_segmented_scene_com_orkut_2026-06-16.md"
)
EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4464_v3_0_m68_triangle_segmented_scene_com_orkut_2026-06-16.json"
)
SNAP_PREP = ROOT / "docs" / "reports" / "goal4464_snap_prepare_com_orkut_2026-06-16.json"
OLD_RTDL = ROOT / "docs" / "reports" / "goal2593_paper_dataset_raw" / "goal2593_eval_com_orkut_rtdl.json"
OLD_CUGRAPH = ROOT / "docs" / "reports" / "goal2593_paper_dataset_raw" / "goal2593_eval_com_orkut_cugraph.json"
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
SCRIPT = ROOT / "scripts" / "v3_0_m66_triangle_segmented_paper_dataset_measure.py"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4464V30M68TriangleSegmentedSceneComOrkutTest(unittest.TestCase):
    def test_evidence_records_com_orkut_segmented_scene_success(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        row = evidence["rows"][0]

        self.assertEqual(4464, evidence["goal"])
        self.assertEqual("v3_0_m68", evidence["milestone"])
        self.assertEqual("segmented_scene_2a1_cupy_paper_dataset", evidence["implementation"])
        self.assertEqual("com_orkut", row["dataset"])
        self.assertEqual(117_185_083, row["edge_count"])
        self.assertEqual(627_584_181, row["expected_triangle_count"])
        self.assertEqual(627_584_181, row["observed_triangle_count"])
        self.assertTrue(row["triangle_count_matches_expected"])
        self.assertFalse(row["global_two_hop_summary_materialized"])
        self.assertFalse(row["global_triangle_scene_materialized"])
        self.assertEqual(117_117_316, row["primitive_count"])
        self.assertEqual(8_579_930_671, row["ray_count"])
        self.assertEqual(59, row["segmentation"]["scene_count"])
        self.assertEqual(1_744, row["segmentation"]["ray_segment_count"])
        self.assertEqual(2_000_000, row["segmentation"]["max_scene_directed_edges"])
        self.assertEqual(2_000_000, row["segmentation"]["max_scene_directed_edge_count"])
        self.assertEqual(279_026_541, row["segmentation"]["max_scene_two_hop_rows"])
        self.assertEqual(1, row["timing_ms"]["query_warmup"])
        self.assertEqual(3, row["timing_ms"]["query_repeat"])

    def test_report_ties_com_orkut_to_old_blockers_and_no_speedup_claim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        prep = json.loads(SNAP_PREP.read_text(encoding="utf-8"))
        old = json.loads(OLD_RTDL.read_text(encoding="utf-8"))
        cugraph = json.loads(OLD_CUGRAPH.read_text(encoding="utf-8"))

        old_failure = old["results"]["com_orkut"]["methods"]["rtdl_2a1"]
        cugraph_row = cugraph["results"]["com_orkut"]["methods"]["cugraph"]
        self.assertEqual("failed", old_failure["status"])
        self.assertIn("68639445368 bytes", old_failure["error"])
        self.assertEqual("ok", cugraph_row["status"])
        self.assertTrue(prep["datasets"]["com_orkut"]["edge_count_matches_snap"])
        self.assertIn("Goal4464", report)
        self.assertIn("com-orkut", report)
        self.assertIn("627,584,181", report)
        self.assertIn("68,639,445,368-byte CUDA allocation request", report)
        self.assertIn("8M and 4M directed-edge scene caps still OOM", report)
        self.assertIn("not a public RTDL-vs-cuGraph", report)

    def test_defaults_and_registries_record_m68_boundary(self) -> None:
        app_source = APP.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("scene_max_directed_edges: int = 2_000_000", app_source)
        self.assertIn("default=2_000_000", app_source)
        self.assertIn("default=2_000_000", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4479.v1", route["version"])
        self.assertIn("Goal4464", route["evidence_refs"])
        self.assertIn("com-orkut", route["current_reader_decision"])
        self.assertIn("prepared ray-batch weighted-sum API", route["next_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4479.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4464", triangle["evidence_refs"])
        self.assertIn("com-orkut", triangle["current_performance_reading"])
        self.assertFalse(triangle["paper_reproduction_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



