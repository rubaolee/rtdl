import json
import unittest
from pathlib import Path

from scripts import goal1746_v1_0_embree_baseline_adapter as adapter


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.md"
MANIFEST = ROOT / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.json"


class Goal1746V10EmbreeBaselineAdapterTest(unittest.TestCase):
    def test_manifest_names_real_v1_0_embree_app_surfaces(self) -> None:
        payload = adapter._write_manifest(REPORT, MANIFEST)
        self.assertEqual(payload["verdict"], "v1_0_embree_baseline_adapter_ready")
        self.assertGreaterEqual(payload["row_count"], 12)
        apps = {row["app"] for row in payload["rows"]}
        for app in (
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertIn(app, apps)

    def test_commands_use_embree_not_optix_profiler_adapter(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for row in payload["rows"]:
            command = row["command"]
            joined = " ".join(command)
            self.assertIn("--backend embree", joined)
            self.assertNotIn("--backend optix", joined)
            self.assertNotIn("goal887_prepared_decision_phase_profiler.py", joined)
            self.assertNotIn("goal933_prepared_segment_polygon_optix_profiler.py", joined)
            self.assertNotIn("goal934_prepared_segment_polygon_pair_rows_optix_profiler.py", joined)
            self.assertNotIn("goal760_optix_robot_pose_flags_phase_profiler.py", joined)

    def test_report_keeps_speedup_boundary_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not fabricate missing phase-profiler rows", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_ann_candidate_uses_rerank_not_full_quality_summary(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        ann = next(row for row in payload["rows"] if row["app"] == "ann_candidate_search")
        command = " ".join(ann["command"])
        self.assertIn("--output-mode rerank_summary", command)
        self.assertNotIn("quality_summary", command)


if __name__ == "__main__":
    unittest.main()
