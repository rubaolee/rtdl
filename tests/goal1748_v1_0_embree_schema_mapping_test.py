import json
import unittest
from pathlib import Path

from scripts.goal1748_v1_0_embree_schema_mapper import (
    REPORT_JSON,
    REPORT_MD,
    build_report,
    write_report,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal1748V10EmbreeSchemaMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_report(build_report())

    def test_report_keeps_claims_blocked(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["verdict"],
            "embree_schema_mapping_ready_without_public_speedup_claim",
        )
        self.assertEqual(payload["row_count"], 14)
        self.assertFalse(payload["public_claim_authorized"])
        self.assertFalse(payload["release_authorized"])

    def test_recovered_ann_is_not_skipped_or_quality_summary(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        ann = next(row for row in payload["rows"] if row["app"] == "ann_candidate_search")
        self.assertTrue(ann["baseline_artifact_present"])
        artifact = ROOT / ann["baseline_artifact"]
        text = artifact.read_text(encoding="utf-8")
        self.assertIn("rerank_summary", text)
        self.assertNotIn("quality_summary", text)
        report = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("7.2 billion", report)

    def test_phase_mapped_rows_are_diagnostic_only(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}
        for app in (
            "road_hazard_screening",
            "hausdorff_distance",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertEqual(rows[app]["classification"], "phase_mapped_diagnostic")
            self.assertGreater(rows[app]["diagnostic_ratio_count"], 0)
            self.assertFalse(rows[app]["direct_speedup_claim_authorized"])
            self.assertFalse(rows[app]["public_claim_authorized"])

    def test_graph_rows_have_no_same_name_current_embree_artifact(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}
        for app in ("graph_visibility_edges", "graph_bfs", "graph_triangle_count"):
            self.assertEqual(rows[app]["classification"], "missing_current_artifact")
            self.assertIn("no same-name current Embree artifact", rows[app]["reason"])

    def test_summary_only_rows_are_not_timing_comparisons(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}
        for app in (
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "segment_polygon_anyhit_rows",
            "segment_polygon_hitcount",
        ):
            self.assertIn(
                rows[app]["classification"],
                {"summary_only", "timing_schema_mismatch"},
            )
            self.assertFalse(rows[app]["public_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
