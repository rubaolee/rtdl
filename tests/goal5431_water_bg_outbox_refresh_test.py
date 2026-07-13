import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5431_water_bg_outbox_refresh.json"
)
AUTHOR_DRAFT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests" / "author_water_bg_input_hash_request.md"
REVIEW_DRAFT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests" / "water_bg_exact_equivalence_review_request.md"
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5431_water_bg_outbox_refresh.py"
)


class Goal5431WaterBgOutboxRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.author = AUTHOR_DRAFT.read_text(encoding="utf-8")
        cls.review = REVIEW_DRAFT.read_text(encoding="utf-8")

    def test_outbox_summary(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5431.water_bg_outbox_refresh.v1",
        )
        self.assertEqual(payload["status"], "water_bg_outbox_refreshed_from_goal5430__prepared_not_sent")
        self.assertEqual(payload["source_goal"], "Goal5430")
        self.assertEqual(len(payload["outbox_files"]), 2)
        self.assertTrue(all(row["send_status"] == "prepared_not_sent" for row in payload["outbox_files"]))

    def test_author_draft_contains_specific_hash_request_and_evidence(self) -> None:
        text = self.author
        self.assertIn("Status: `prepared_not_sent`", text)
        self.assertIn("USADetailedWaterBodies.wkt bytes or sha256", text)
        self.assertIn("USACensusBlockGroupBoundaries.wkt bytes or sha256", text)
        self.assertIn("num_points_cell=8", text)
        self.assertIn("0.896436750888824", text)
        self.assertIn("0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39", text)
        self.assertIn("8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e", text)
        self.assertIn("No exact paper dataset claim is made.", text)

    def test_review_draft_contains_exact_equivalence_choices_and_default(self) -> None:
        text = self.review
        self.assertIn("Status: `prepared_not_sent`", text)
        self.assertIn("exact-equivalent", text)
        self.assertIn("bounded_public_reconstruction_only_keep_level_b", text)
        self.assertIn("not_accepted_keep_level_b", text)
        self.assertIn("Point counts, MBRs, and HDResult alone are not treated as proof", text)
        self.assertIn("WaterBodies generated WKT sha256", text)
        self.assertIn("BlockGroups generated WKT sha256", text)

    def test_claim_boundary_remains_not_sent_and_not_exact(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["outbox_refreshed"])
        self.assertFalse(boundary["request_sent_claimed"])
        self.assertFalse(boundary["external_artifacts_acquired"])
        self.assertFalse(boundary["exact_equivalence_accepted"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_pod_execution_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["explicit_lb_reopened"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])

    def test_stop_loss_gate_fields_present_and_passing(self) -> None:
        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertNotEqual(gate["gate_non_app_consumer"].lower(), "none")
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

    def test_builder_is_outbox_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
