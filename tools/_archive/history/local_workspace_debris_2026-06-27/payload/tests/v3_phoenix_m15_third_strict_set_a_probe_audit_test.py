import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.json"
)
REPORT_PATH = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md"
)
CALL_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md"
)


class V3PhoenixM15ThirdStrictSetAProbeAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.call = CALL_PATH.read_text(encoding="utf-8")

    def test_m15_selects_triangle_without_counting_it_yet(self):
        self.assertEqual(
            self.payload["status"],
            "m15_triangle_selected_for_m16_by_2ai_not_release",
        )
        decision = self.payload["m15_decision"]
        self.assertEqual(decision["selected_candidate"], "triangle_counting")
        self.assertEqual(decision["selected_capability"], "prepared_graph_chunk_non_graph_stream")
        self.assertFalse(decision["counts_as_third_strict_set_a_material_probe_now"])
        self.assertIn("runtime_executed=true", decision["reason_not_counted_now"])
        self.assertIn("M16 local runner wiring", decision["next_required_work"])
        consensus = self.payload["m15_2ai_consensus"]
        self.assertEqual(
            consensus["status"],
            "accept_m15_triangle_m16_local_runner_wiring_no_pod",
        )
        self.assertFalse(consensus["triangle_counts_as_third_strict_set_a_material_probe_now"])
        self.assertTrue(consensus["triangle_next_local_implementation_target"])
        self.assertEqual(consensus["blockers_or_p1_fixes"], [])

    def test_claim_flags_and_pod_spend_are_blocked(self):
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "true_zero_copy_claim_authorized",
            "external_embedding_or_zero_copy_claim_authorized",
            "focused_pod_spend_authorized_now",
            "all_app_pod_spend_authorized",
        ):
            self.assertFalse(self.payload[key], key)
        self.assertIn("focused_pod_spend_authorized_now: false", self.report)
        self.assertIn("all_app_pod_spend_authorized: false", self.call)

    def test_triangle_has_real_source_but_clear_blockers(self):
        triangle = self.payload["candidate_assessments"][0]
        self.assertEqual(triangle["candidate"], "triangle_counting")
        self.assertTrue(triangle["set_a_member"])
        self.assertIn("device-output stream continuation", triangle["physical_runtime_source"])
        self.assertAlmostEqual(triangle["old_row_numbers"]["hot_optix_over_embree"], 347.23219125688223)
        self.assertAlmostEqual(triangle["old_row_numbers"]["wall_optix_over_embree"], 6.342008514587283)
        blockers = set(triangle["blockers_before_strict_credit"])
        self.assertIn("not_yet_current_prepared_execution_session_runner_path", blockers)
        self.assertIn("m113_cuda_graph_capture_still_blocked", blockers)
        self.assertIn("not_rt_graph_paper_reproduction", blockers)
        self.assertEqual(
            triangle["m15_classification"],
            "best_candidate_for_m16_local_runner_wiring_not_yet_third_probe",
        )

    def test_alternatives_are_not_over_counted(self):
        classifications = {
            item["candidate"]: item["m15_classification"]
            for item in self.payload["candidate_assessments"]
        }
        self.assertEqual(
            classifications["hausdorff_xhd"],
            "positive_focused_evidence_but_too_small_for_third_strict_probe",
        )
        self.assertEqual(classifications["rt_dbscan"], "structural_only_not_candidate_now")
        self.assertEqual(
            classifications["rayjoin_pip_or_lsi"],
            "coverage_or_structural_only_not_candidate_now",
        )

    def test_review_request_asks_for_no_pod_local_next_step(self):
        self.assertIn("accept_m15_triangle_m16_local_runner_wiring_no_pod", self.call)
        self.assertIn("focused POD authorization now: yes/no", self.call)
        self.assertIn("Triangle counts as the third strict Set-A material probe now", self.call)
        self.assertIn("Please be strict", self.call)
        self.assertIn("Was I foolish?", self.report)
        self.assertIn("Was I foolish?", self.call)
        self.assertIn("accept_m15_triangle_m16_local_runner_wiring_no_pod", self.report)


if __name__ == "__main__":
    unittest.main()
