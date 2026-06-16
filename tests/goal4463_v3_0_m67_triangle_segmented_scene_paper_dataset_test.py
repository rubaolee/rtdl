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
    / "goal4463_v3_0_m67_triangle_segmented_scene_soc_livejournal1_2026-06-16.md"
)
EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4463_v3_0_m67_triangle_segmented_scene_soc_livejournal1_2026-06-16.json"
)
SNAP_PREP = ROOT / "docs" / "reports" / "goal4463_snap_prepare_soc_livejournal1_2026-06-16.json"
OLD_RTDL = ROOT / "docs" / "reports" / "goal2593_paper_dataset_raw" / "goal2593_eval_soc_lj_rtdl.json"
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4463V30M67TriangleSegmentedScenePaperDatasetTest(unittest.TestCase):
    def test_evidence_records_soc_livejournal1_segmented_scene_success(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        row = evidence["rows"][0]

        self.assertEqual(4463, evidence["goal"])
        self.assertEqual("segmented_scene_2a1_cupy_paper_dataset", evidence["implementation"])
        self.assertEqual("soc_livejournal1", row["dataset"])
        self.assertEqual(68_993_773, row["edge_count"])
        self.assertEqual(285_730_264, row["expected_triangle_count"])
        self.assertEqual(285_730_264, row["observed_triangle_count"])
        self.assertTrue(row["triangle_count_matches_expected"])
        self.assertFalse(row["global_two_hop_summary_materialized"])
        self.assertFalse(row["global_triangle_scene_materialized"])
        self.assertEqual(6, row["segmentation"]["scene_count"])
        self.assertEqual(280, row["segmentation"]["ray_segment_count"])
        self.assertEqual(1_383_299_326, row["segmentation"]["total_two_hop_rows"])

    def test_report_ties_segmented_scenes_to_goal2593_scene_scale_blocker(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        old = json.loads(OLD_RTDL.read_text(encoding="utf-8"))
        prep = json.loads(SNAP_PREP.read_text(encoding="utf-8"))

        old_failure = old["results"]["soc_livejournal1"]["methods"]["rtdl_2a1"]
        self.assertEqual("failed", old_failure["status"])
        self.assertIn("11066394608 bytes", old_failure["error"])
        self.assertTrue(prep["datasets"]["soc_livejournal1"]["edge_count_matches_snap"])
        self.assertIn("Goal4463", report)
        self.assertIn("source-range triangle-scene segmentation", report)
        self.assertIn("285,730,264", report)
        self.assertIn("global triangle scene", report)
        self.assertIn("not a public speedup claim", report)

    def test_app_and_registries_record_m67_boundary(self) -> None:
        app_source = APP.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("rt_graph_2a1_segmented_scene_generic_rt", app_source)
        self.assertIn("_plan_rt_graph_2a1_cupy_source_scene_segments", app_source)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4463.v1", route["version"])
        self.assertIn("Goal4463", route["evidence_refs"])
        self.assertIn("soc-LiveJournal1", route["current_reader_decision"])
        self.assertIn("com-orkut", route["next_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4463.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4463", triangle["evidence_refs"])
        self.assertIn("soc-LiveJournal1", triangle["current_performance_reading"])
        self.assertFalse(triangle["paper_reproduction_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
