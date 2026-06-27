import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "10_triangle_prepared_graph_chunk.md"


class V3PhoenixTrianglePreparedGraphTutorialCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_tutorial_candidate_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "triangle_prepared_graph_tutorial_candidate_not_m7",
        )
        self.assertEqual(self.payload["generic_capability"], "prepared_graph_chunk")
        self.assertEqual(
            self.payload["generic_capability_status"],
            "candidate_executor_linkage_not_closed",
        )
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["paper_reproduction_claim_authorized"])
        self.assertFalse(self.payload["graph_database_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)

    def test_rows_keep_hot_and_wall_ratios_together(self):
        rows = {
            row["comparison_group"]: row for row in self.payload["rows"]
        }
        small = rows["triangle_count_rt_graph_2a1_cliques_20000"]
        large = rows["triangle_count_rt_graph_2a1_cliques_80000"]
        self.assertAlmostEqual(small["hot_optix_over_embree"], 116.05985639108538)
        self.assertAlmostEqual(small["wall_optix_over_embree"], 1.6768981818785074)
        self.assertEqual(small["oracle_triangle_count"], 80000)
        self.assertAlmostEqual(large["hot_optix_over_embree"], 347.23219125688223)
        self.assertAlmostEqual(large["wall_optix_over_embree"], 6.342008514587283)
        self.assertEqual(large["oracle_triangle_count"], 320000)
        for row in rows.values():
            self.assertIn("not graph database or paper dataset", row["synthetic_fixture_boundary"])
            self.assertGreater(row["hot_optix_over_embree"], row["wall_optix_over_embree"])

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("synthetic_k4_clique_ladder_not_paper_dataset", blockers)
        self.assertIn("prepared_graph_chunk_executor_linkage_not_closed", blockers)
        self.assertIn("hot_query_vs_wall_timing_ratio_not_characterized_for_release", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("Triangle V3 is 347x faster end to end", forbidden)
        self.assertIn("RTDL reproduces the RT-Graph paper", forbidden)
        self.assertIn("RTDL accelerates graph databases", forbidden)
        self.assertIn("Triangle is M7-qualified", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        for text in (self.text, self.tutorial):
            self.assertIn("116.060x", text)
            self.assertIn("347.232x", text)
            self.assertIn("1.677x", text)
            self.assertIn("6.342x", text)
            self.assertIn("not a release", text)
            self.assertIn("Do not claim Triangle V3 is 347x faster end to end", text)
            self.assertIn("Do not claim RTDL reproduces the RT-Graph paper", text)
        self.assertIn("Do not claim prepared_graph_chunk executor linkage is closed", self.text)
        self.assertIn("Do not claim M113 graph capture is ready", self.tutorial)
        self.assertIn("Do not claim automatic partner selection", self.tutorial)
        self.assertIn("Was I foolish?", self.text)
        self.assertIn("No. The underlying intake already has 2-AI", self.text)


if __name__ == "__main__":
    unittest.main()
