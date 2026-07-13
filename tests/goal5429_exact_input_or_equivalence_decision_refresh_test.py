import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5429_exact_input_or_equivalence_decision_refresh.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py"
)


class Goal5429ExactInputOrEquivalenceDecisionRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_level_b_matrix_status_is_preserved(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5429.exact_input_or_equivalence_decision_refresh.v1",
        )
        self.assertEqual(
            payload["status"],
            "exact_input_or_equivalence_decision_refreshed_after_goal5428__no_route_work",
        )
        matrix = payload["level_b_matrix_status"]
        self.assertTrue(matrix["matched"])
        self.assertEqual(matrix["total_case_count"], 6)
        self.assertEqual(matrix["total_route_result_count"], 9)
        self.assertEqual(matrix["full_public_geo_case_count"], 1)
        self.assertEqual(matrix["strongest_new_row"], "geo_water_bg_full_public_paper_config")

    def test_full_reproduction_blocker_is_exact_input_or_equivalence(self) -> None:
        decision = self.summary["full_reproduction_decision"]
        self.assertEqual(
            decision["full_reproduction_next_blocker"],
            "exact_input_artifacts_or_explicit_exact_equivalence_acceptance",
        )
        self.assertFalse(decision["more_route_performance_work_is_next"])
        self.assertFalse(decision["route_micro_optimization_authorized"])
        self.assertFalse(decision["explicit_lb_authorized"])

    def test_exact_equivalence_protocol_rejects_statistics_only(self) -> None:
        protocol = self.summary["exact_or_equivalence_requirements"]
        required = set(protocol["required_before_exact_equivalence_can_be_considered"])
        not_sufficient = set(protocol["not_sufficient"])
        self.assertIn("generated input file sha256 recorded in artifact", required)
        self.assertIn(
            "external review explicitly accepts the generated public inputs as exact-equivalent or accepts a renamed bounded public-reconstruction claim",
            required,
        )
        self.assertIn("matching point counts", not_sufficient)
        self.assertIn("matching MBRs", not_sufficient)
        self.assertIn("matching HDResult alone", not_sufficient)

    def test_current_best_candidate_is_not_promoted_to_exact(self) -> None:
        candidate = self.summary["current_best_exact_equivalence_candidate"]
        self.assertEqual(candidate["row_id"], "geo_waterbodies_blockgroups")
        self.assertEqual(candidate["goal5428_row_id"], "geo_water_bg_full_public_paper_config")
        self.assertEqual(candidate["evidence_level"], "level_b_full_public_same_source_geo_not_exact_file_hash")
        self.assertIn("No author WKT file hashes.", candidate["why_not_exact_yet"])
        self.assertIn("No byte-identical regeneration proof.", candidate["why_not_exact_yet"])

    def test_claim_boundary_and_rejected_paths(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["decision_refresh_claimed"])
        self.assertTrue(boundary["level_b_matrix_current_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["new_pod_execution_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

        blocked = {row["path"]: row for row in self.summary["blocked_or_rejected_paths"]}
        self.assertFalse(blocked["route_micro_optimization"]["allowed"])
        self.assertFalse(blocked["explicit_lb_or_row_identity_work"]["allowed"])
        self.assertFalse(blocked["water_bg_exact_promotion_by_statistics_only"]["allowed"])
        self.assertFalse(blocked["performance_ratio_from_goal5428"]["allowed"])

    def test_next_work_is_review_or_provenance_not_pod_execution(self) -> None:
        branches = [row["branch"] for row in self.summary["branch_ranking"]]
        self.assertEqual(branches[0], "strict_review_goals5424_5428_packet")
        self.assertIn("author_artifact_or_hash_acquisition", branches)
        self.assertIn("water_bg_public_reconstruction_exact_equivalence_review_packet", branches)
        self.assertEqual(
            self.summary["recommended_next_goal"],
            "Goal5430_water_bg_exact_equivalence_review_packet_or_author_artifact_request",
        )
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])

    def test_stop_loss_gate_fields_present_and_passing(self) -> None:
        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertNotEqual(gate["gate_non_app_consumer"].lower(), "none")
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_builder_is_decision_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
