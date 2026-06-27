import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "15_contact_manifold_broadphase_boundary.md"


class V3PhoenixContactManifoldBroadphaseBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_boundary_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "contact_manifold_broadphase_boundary_not_m7",
        )
        self.assertEqual(self.payload["generic_capability"], "aabb_candidate_stream")
        self.assertEqual(self.payload["secondary_capability"], "bounded_witness_collection")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["full_contact_solver_claim_authorized"])
        self.assertFalse(self.payload["physics_solver_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)
        self.assertEqual(
            self.payload["current_packet_external_review_status"],
            "claude_approved_boundary_not_m7",
        )
        self.assertEqual(
            self.payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_no_m7_promotion",
        )

    def test_row_preserves_reference_pass_and_wall_boundary(self):
        row = self.payload["candidate_row"]
        self.assertEqual(row["app_id"], "contact_manifold")
        self.assertEqual(row["comparison_group"], "generic_aabb_broadphase_collect_k")
        self.assertEqual(row["candidate_discovery_primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(row["candidate_discovery_contract"], "generic_aabb_intersection_pair_rows_2d")
        self.assertEqual(row["primitive_under_test"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            row["query_metric_scope"],
            "emit_aabb_intersection_pair_rows_2d_only_not_wall_not_full_contact_solver",
        )
        self.assertTrue(row["matches_cpu_reference"])
        self.assertFalse(row["overflowed"])
        self.assertEqual(row["valid_count"], 4096)
        self.assertEqual(row["phase_validation_status"], "accept")
        self.assertAlmostEqual(row["query_optix_over_embree"], 1.2348474960917915)
        self.assertAlmostEqual(row["collect_k_optix_over_embree"], 2.7590511659809116)
        self.assertAlmostEqual(row["prepare_aabb_index_optix_over_embree"], 0.24317940095569324)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 0.8029757821318222)
        self.assertLess(row["prepare_aabb_index_optix_over_embree"], 1.0)
        self.assertLess(row["wall_optix_over_embree"], 1.0)

    def test_paired_v2_context_blocks_broad_claim(self):
        context = self.payload["paired_v2_v3_context"]
        self.assertAlmostEqual(context["app_geomean_speedup_vs_v2_14"], 0.9964547635407576)
        self.assertTrue(context["paired_rows_are_standard_goal2626_rows"])
        self.assertAlmostEqual(context["embree_v3_speedup_vs_v2_14"], 1.0037013324521886)
        self.assertAlmostEqual(context["optix_v3_speedup_vs_v2_14"], 0.9892605137398928)

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("wall_timing_optix_slower_than_embree", blockers)
        self.assertIn("full_contact_solver_not_claimed", blockers)
        self.assertIn("broadphase_candidate_discovery_only", blockers)
        self.assertIn("optix_prepare_aabb_index_cost_offsets_hot_query_gain", blockers)
        self.assertIn("standard_paired_v2_v3_rows_are_parity_or_regression", blockers)
        self.assertIn("aabb_index_preparation_optix_4x_slower_fix_required_before_candidacy", blockers)
        self.assertIn("overflow_path_larger_dataset_not_validated", blockers)
        self.assertIn("future_public_row_review_required_before_m7", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("Contact Manifold V3 is 1.235x faster end to end", forbidden)
        self.assertIn("RTDL accelerates the full contact solver", forbidden)
        self.assertIn("contact_manifold is M7-qualified", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        for text in (self.text, self.tutorial):
            self.assertIn("1.235x", text)
            self.assertIn("2.759x", text)
            self.assertIn("0.803x", text)
            self.assertIn("matches_cpu_reference: true", text)
            self.assertIn("Do not claim Contact Manifold V3 is 1.235x faster end to end", text)
            self.assertIn("Do not claim RTDL accelerates the full contact solver", text)
            self.assertIn("not a release", text)
            self.assertIn("not full contact-solver throughput", text)
            self.assertIn("overflow", text)
        self.assertIn("Was I foolish?", self.text)
        self.assertNotIn("physics-engine throughput", self.tutorial)


if __name__ == "__main__":
    unittest.main()
