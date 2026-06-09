from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3054_v2_6_machine_readable_partner_choice_guidance_2026-06-02.md"


class Goal3054V26PartnerChoiceGuidanceTest(unittest.TestCase):
    def test_guidance_validates_and_covers_all_promoted_benchmark_apps(self) -> None:
        guidance = rt.v2_6_partner_choice_guidance()
        validation = rt.validate_v2_6_partner_choice_guidance(guidance, repo_root=ROOT)

        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(rt.V2_6_PARTNER_CHOICE_GUIDANCE_VERSION, guidance["guidance_version"])
        self.assertEqual(10, guidance["app_count"])
        self.assertEqual(10, guidance["row_count"])
        self.assertEqual(
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
            {row["benchmark_app"] for row in guidance["rows"]},
        )
        self.assertIn("users_choose", guidance["partner_choice_rule"])
        self.assertFalse(guidance["automatic_partner_selection_allowed"])
        self.assertFalse(guidance["public_speedup_claim_authorized"])
        self.assertFalse(guidance["rt_core_speedup_claim_authorized"])
        self.assertFalse(guidance["broad_partner_speedup_claim_authorized"])
        self.assertFalse(guidance["true_zero_copy_claim_authorized"])
        self.assertFalse(guidance["release_authorized"])
        self.assertFalse(guidance["app_specific_native_engine_logic_authorized"])

    def test_numba_recommendations_are_specific_not_global(self) -> None:
        raydb = rt.plan_v2_6_partner_choice("raydb_style", "unfused_grouped_minmax_count_sum_avg")
        rayjoin = rt.plan_v2_6_partner_choice("spatial_rayjoin", "row_stream_compact_mask")
        triangle = rt.plan_v2_6_partner_choice("triangle_counting", "candidate_row_compact_mask")

        for plan in (raydb, rayjoin, triangle):
            self.assertEqual("single_recommendation", plan["status"])
            self.assertEqual("numba", plan["recommended_partner"])
            self.assertFalse(plan["auto_select_partner_allowed"])
            self.assertIn("Numba", plan["matches"][0]["numba_role"])
            self.assertIn("Goal", plan["matches"][0]["evidence_goal"])

        self.assertIn("raydb_numba_minmax_1m.json", raydb["matches"][0]["evidence_artifact"])
        self.assertIn("rayjoin_numba_compact_mask_1m.json", rayjoin["matches"][0]["evidence_artifact"])
        self.assertIn("triangle_numba_compact_mask_1m.json", triangle["matches"][0]["evidence_artifact"])
        self.assertIn("generic RT graph relationship-count composition", triangle["matches"][0]["primitive_first_path"])
        self.assertNotIn("native scalar triangle-count primitive", triangle["matches"][0]["primitive_first_path"])

    def test_cupy_numba_and_primitive_rows_remain_recommended_where_evidence_says_so(self) -> None:
        hausdorff = rt.plan_v2_6_partner_choice("hausdorff_xhd", "active_frontier_exact_distance")
        dbscan = rt.plan_v2_6_partner_choice("rt_dbscan", "component_labeling")
        barnes_hut = rt.plan_v2_6_partner_choice("barnes_hut", "force_vector_continuation")
        rtnn = rt.plan_v2_6_partner_choice("rtnn", "ranked_summary_quality_probe")

        self.assertEqual("rtdl_primitive", hausdorff["recommended_partner"])
        self.assertIn("CuPy", hausdorff["matches"][0]["cupy_role"])
        self.assertIn("not the current default", hausdorff["matches"][0]["numba_role"])
        self.assertEqual("numba", dbscan["recommended_partner"])
        self.assertIn("grouped-stream", dbscan["matches"][0]["numba_role"])
        self.assertIn("Goal3918", dbscan["matches"][0]["evidence_goal"])
        self.assertIn("goal3859_rt_dbscan_numba_grouped_stream_a5000", dbscan["matches"][0]["evidence_artifact"])
        self.assertEqual("cupy", barnes_hut["recommended_partner"])
        self.assertIn("no-RawKernel", barnes_hut["matches"][0]["numba_role"])
        self.assertIn("Goal3837", barnes_hut["matches"][0]["evidence_goal"])
        self.assertEqual("rtdl_primitive", rtnn["recommended_partner"])

    def test_no_promoted_partner_and_unknown_rows_fail_closed(self) -> None:
        robot = rt.plan_v2_6_partner_choice("robot_collision", "pose_collision_flag_reduction")
        contact = rt.plan_v2_6_partner_choice("contact_manifold", "bounded_witness_filtering")
        librts = rt.plan_v2_6_partner_choice("librts_spatial_index", "mutable_index_query_policy")
        unknown = rt.plan_v2_6_partner_choice("new_app", "custom_logic")

        for plan in (robot, contact, librts):
            self.assertEqual("none", plan["recommended_partner"])
            self.assertIn("not promoted", plan["matches"][0]["numba_role"])
            self.assertFalse(plan["auto_select_partner_allowed"])

        self.assertEqual("no_measured_guidance", unknown["status"])
        self.assertEqual("none", unknown["recommended_partner"])
        self.assertFalse(unknown["auto_select_partner_allowed"])
        self.assertIn("same-contract evidence", unknown["recommendation"])

    def test_explain_helper_respects_user_choice_without_auto_selecting(self) -> None:
        accepted = rt.explain_v2_6_partner_choice(
            "spatial_rayjoin",
            "row_stream_compact_mask",
            user_preferred_partner="numba",
        )
        caution = rt.explain_v2_6_partner_choice(
            "spatial_rayjoin",
            "row_stream_compact_mask",
            user_preferred_partner="cupy",
        )

        self.assertTrue(accepted["user_choice_remains_authority"])
        self.assertFalse(accepted["auto_select_partner_allowed"])
        self.assertIn("matches the current recommendation", " ".join(accepted["explain_notes"]))
        self.assertIn("new same-contract evidence", " ".join(caution["explain_notes"]))

    def test_docs_report_roadmap_and_exports_are_consistent(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md").read_text(encoding="utf-8")
        roadmap = rt.v2_6_roadmap()
        roadmap_validation = rt.validate_v2_6_roadmap(roadmap, repo_root=ROOT)

        self.assertIn("Goal3054", report)
        self.assertIn("current_benchmark_adequacy", docs)
        self.assertIn("current_benchmark_adequacy", matrix)
        self.assertIn("Partner-Needed Continuations", matrix)
        self.assertIn("Primitive-First Paths", matrix)
        self.assertNotIn("native scalar triangle-count primitive", docs)
        self.assertNotIn("native scalar triangle-count primitive", matrix)
        self.assertEqual("Goal3054", roadmap["partner_choice_guidance_goal"])
        self.assertEqual("accept", roadmap_validation["status"], roadmap_validation["errors"])
        for name in (
            "v2_6_partner_choice_guidance",
            "plan_v2_6_partner_choice",
            "explain_v2_6_partner_choice",
            "validate_v2_6_partner_choice_guidance",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)


if __name__ == "__main__":
    unittest.main()
