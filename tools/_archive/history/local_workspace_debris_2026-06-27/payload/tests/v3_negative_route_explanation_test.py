import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "rebuild" / "v3" / "v3_negative_route_explanations_2026-06-20.md"
CLASSIFICATION = ROOT / "docs" / "rebuild" / "v3" / "v3_benchmark_app_classification_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md"
PERF_MODEL = ROOT / "docs" / "performance_model.md"


class V3NegativeRouteExplanationTest(unittest.TestCase):
    def test_explanation_doc_names_fixture_scope_and_non_claims(self):
        text = DOC.read_text(encoding="utf-8")
        required = [
            "rayjoin_all_backend_query_summary",
            "aabb_index_all_count_only",
            "0.03414924661592695x",
            "0.06539687665395033x",
            "br_county_subset.cdb",
            "row_count=1",
            "row_count=0",
            "row_count=6",
            "warmup=0",
            "repeat=1",
            "paper_reproduction: false",
            "paper_equivalent_dataset: false",
            "not a LibRTS paper reproduction",
            "not a RayJoin paper-scale performance row",
            "aabb_index_all_count_only_large_32768",
            "814.3388221324167x",
            "without LibRTS paper/authors-code wording",
            "never compare them to RayJoin or LibRTS paper results",
        ]
        for needle in required:
            self.assertIn(needle, text)

    def test_classification_carries_negative_route_explanations(self):
        payload = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
        spatial = payload["apps"]["spatial_rayjoin"]["negative_route_explanation"]
        self.assertEqual(spatial["row"], "rayjoin_all_backend_query_summary")
        self.assertFalse(spatial["paper_result_comparison_allowed"])
        self.assertTrue(any("row_count=1" in item for item in spatial["why_slow"]))
        self.assertTrue(any("warmup=0" in item for item in spatial["why_slow"]))

        librts = payload["apps"]["librts_spatial_index"]["negative_route_explanation"]
        self.assertEqual(librts["row"], "aabb_index_all_count_only")
        self.assertFalse(librts["paper_result_comparison_allowed"])
        self.assertTrue(any("paper_equivalent_dataset=false" in item for item in librts["why_slow"]))
        self.assertTrue(any("box_count=1024" in item for item in librts["why_slow"]))

    def test_public_rebuild_docs_link_the_explanation(self):
        for path in [REPORT, PERF_MODEL]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("v3_negative_route_explanations_2026-06-20.md", text)
            self.assertIn("paper", text.lower())
            self.assertIn("not", text.lower())


if __name__ == "__main__":
    unittest.main()
