import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5430_water_bg_exact_equivalence_packet.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5430_water_bg_exact_equivalence_packet.py"
)


class Goal5430WaterBgExactEquivalencePacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_packet_status_and_case(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5430.water_bg_exact_equivalence_packet.v1",
        )
        self.assertEqual(
            payload["status"],
            "water_bg_exact_equivalence_packet_ready__await_external_decision_or_author_artifacts",
        )
        case = payload["case"]
        self.assertEqual(case["case_id"], "geo_water_bg_full_public_paper_config")
        self.assertEqual(case["paper_pair"], "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt")
        self.assertEqual(case["input_identity_level"], "level_b_full_public_same_source_geo_not_exact_file_hash")
        self.assertEqual(case["paper_config"]["num_points_cell"], 8)
        self.assertTrue(case["paper_config"]["matches_paper_log"])

    def test_public_reconstruction_evidence_is_specific(self) -> None:
        evidence = self.summary["public_reconstruction_evidence"]
        water = evidence["waterbodies"]
        bg = evidence["blockgroups"]
        self.assertEqual(water["paper_basename"], "USADetailedWaterBodies.wkt")
        self.assertEqual(bg["paper_basename"], "USACensusBlockGroupBoundaries.wkt")
        self.assertEqual(water["generated_wkt_sha256"], "0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39")
        self.assertEqual(bg["generated_wkt_sha256"], "8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e")
        self.assertEqual(water["point_count_delta"], 6129)
        self.assertEqual(bg["point_count_delta"], 127)
        self.assertLess(water["max_abs_mbr_delta"], 1e-5)
        self.assertLess(bg["max_abs_mbr_delta"], 1e-5)
        self.assertTrue(evidence["summary"]["still_not_exact"])

    def test_author_and_rtdl_value_evidence_preserved(self) -> None:
        case = self.summary["case"]
        self.assertAlmostEqual(case["paper_config"]["hd_result"], 0.8964367508888245, places=12)
        rtdl = case["rtdl_exact_witness"]
        self.assertAlmostEqual(rtdl["hd_result_float64"], 0.8964380566690101, places=12)
        self.assertLessEqual(rtdl["abs_diff_vs_author"], rtdl["comparison_tolerance"])
        self.assertTrue(rtdl["matched_with_declared_tolerance"])
        self.assertTrue(rtdl["per_source_witness_exact"])
        self.assertAlmostEqual(rtdl["same_witness_float32_distance"], 0.8964367508888245, places=12)

    def test_request_and_review_packet_are_actionable_but_not_claiming_exact(self) -> None:
        request = self.summary["author_artifact_request"]
        self.assertEqual(request["preferred_hash_algorithm"], "sha256")
        request_text = "\n".join(request["request_items"])
        self.assertIn("USADetailedWaterBodies.wkt", request_text)
        self.assertIn("USACensusBlockGroupBoundaries.wkt", request_text)
        self.assertIn("source URLs", request_text)
        self.assertIn("num_points_cell=8", request_text)

        review = self.summary["external_exact_equivalence_review_packet"]
        self.assertIn("statistics and scalar agreement", "\n".join(review["evidence_against_acceptance"]).lower())
        self.assertIn("bounded_public_reconstruction_only_keep_level_b", review["allowed_review_outcomes"])
        self.assertEqual(
            review["recommended_default_without_external_acceptance"],
            "bounded_public_reconstruction_only_keep_level_b",
        )

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["packet_claimed"])
        self.assertTrue(boundary["author_artifact_request_prepared"])
        self.assertTrue(boundary["exact_equivalence_review_packet_prepared"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["exact_equivalence_accepted_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["new_pod_execution_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

    def test_decision_matrix_and_pod_expectation(self) -> None:
        matrix = self.summary["decision_matrix"]
        conditions = "\n".join(row["condition"] for row in matrix)
        self.assertIn("author WKT files", conditions)
        self.assertIn("byte-identical regeneration", conditions)
        self.assertIn("external exact-equivalence accepted", conditions)
        self.assertIn("no artifacts and no exact-equivalence", conditions)
        no_artifacts = [row for row in matrix if row["condition"].startswith("no artifacts")][0]
        self.assertFalse(no_artifacts["pod_expected"])
        self.assertIn("Level-B", no_artifacts["next"])
        self.assertFalse(self.summary["pod_usage"]["used"])
        self.assertFalse(self.summary["pod_usage"]["expected_next"])

    def test_stop_loss_gate_fields_present_and_passing(self) -> None:
        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertNotEqual(gate["gate_non_app_consumer"].lower(), "none")
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_builder_is_packet_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
