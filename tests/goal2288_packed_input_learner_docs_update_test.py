from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
V2_APP = ROOT / "docs" / "tutorials" / "v2_app_building.md"
SEGMENT_POLYGON = ROOT / "docs" / "tutorials" / "segment_polygon_workloads.md"
REPORT = ROOT / "docs" / "reports" / "goal2288_packed_input_learner_docs_update_2026-05-17.md"


class Goal2288PackedInputLearnerDocsUpdateTest(unittest.TestCase):
    def test_v2_app_building_teaches_prepared_packed_pattern(self) -> None:
        text = V2_APP.read_text(encoding="utf-8")

        self.assertIn("## Reuse Prepared And Packed Inputs", text)
        self.assertIn("prepare static build-side geometry once", text)
        self.assertIn("pack reusable probe/query geometry once", text)
        self.assertIn("prepare_segment_pair_intersection_optix", text)
        self.assertIn("pack_segments(records=left_segments)", text)
        self.assertIn("not a promise that", text)
        self.assertIn("every workload gets a 20x gain", text)

    def test_segment_polygon_tutorial_links_to_pattern_with_boundary(self) -> None:
        text = SEGMENT_POLYGON.read_text(encoding="utf-8")

        self.assertIn("## Repeated OptiX Calls", text)
        self.assertIn("v2_app_building.md#reuse-prepared-and-packed-inputs", text)
        self.assertIn("repacking a large Python", text)
        self.assertIn("not a broad", text)
        self.assertIn("RayJoin speedup claim", text)

    def test_report_lists_updates_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("learner-facing", text)
        self.assertIn("docs", text)
        self.assertIn("docs/tutorials/v2_app_building.md", text)
        self.assertIn("docs/tutorials/segment_polygon_workloads.md", text)
        self.assertIn("do not claim final v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
