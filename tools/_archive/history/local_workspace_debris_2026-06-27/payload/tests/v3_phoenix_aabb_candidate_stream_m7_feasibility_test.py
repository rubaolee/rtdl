import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "12_aabb_candidate_stream.md"


class V3PhoenixAABBCandidateStreamM7FeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_feasibility_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "aabb_candidate_stream_m7_feasibility_not_promoted",
        )
        self.assertEqual(self.payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["paper_reproduction_claim_authorized"])
        self.assertFalse(self.payload["librts_authors_code_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)

    def test_candidate_row_preserves_strong_signal_and_scope(self):
        row = self.payload["candidate_row"]
        self.assertEqual(row["app_id"], "librts_spatial_index")
        self.assertEqual(row["comparison_group"], "aabb_index_all_count_only_large_32768")
        self.assertEqual(row["generic_primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(row["primitive_contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(row["box_count"], 32768)
        self.assertEqual(row["point_query_count"], 32768)
        self.assertEqual(row["box_query_count"], 32768)
        self.assertFalse(row["paper_equivalent_dataset"])
        self.assertFalse(row["authors_code_comparison"])
        self.assertTrue(row["cpu_reference_skipped"])
        self.assertIsNone(row["matches_cpu_reference"])
        self.assertTrue(row["counts_match_between_backends"])
        self.assertAlmostEqual(row["query_optix_over_embree"], 814.3388221324167)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 132.75317674847796)
        self.assertAlmostEqual(row["elapsed_optix_over_embree"], 73.82647454204714)
        self.assertEqual(row["counts"]["point_contains"], 46343760)
        self.assertEqual(row["counts"]["range_contains"], 32302908)
        self.assertEqual(row["counts"]["range_intersects"], 70429254)

    def test_paired_v2_context_blocks_broad_v2_claim(self):
        context = self.payload["paired_v2_v3_context"]
        self.assertAlmostEqual(context["app_geomean_speedup_vs_v2_14"], 1.1629427337471825)
        self.assertTrue(context["paired_rows_are_small_standard_rows"])
        self.assertTrue(context["large_32768_v2_14_same_row_absent"])
        self.assertAlmostEqual(context["small_embree_v3_speedup_vs_v2"], 1.2061962735375036)
        self.assertAlmostEqual(context["small_optix_v3_speedup_vs_v2"], 1.1212402422774685)

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("cpu_reference_skipped_and_matches_reference_null", blockers)
        self.assertIn("paper_equivalent_dataset_false", blockers)
        self.assertIn("large_32768_v2_14_same_row_absent", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("RTDL reproduces the LibRTS paper", forbidden)
        self.assertIn("RTDL beats LibRTS authors code", forbidden)
        self.assertIn("V3 is 814x faster than V2", forbidden)
        self.assertIn("Generic AABB count-only proves full spatial-index acceleration", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        for text in (self.text, self.tutorial):
            self.assertIn("814.339x", text)
            self.assertIn("132.753x", text)
            self.assertIn("Do not claim RTDL reproduces the LibRTS paper", text)
            self.assertIn("Do not claim V3 is 814x faster than V2", text)
            self.assertIn("not a release", text)
        self.assertIn("Was I foolish?", self.text)


if __name__ == "__main__":
    unittest.main()
