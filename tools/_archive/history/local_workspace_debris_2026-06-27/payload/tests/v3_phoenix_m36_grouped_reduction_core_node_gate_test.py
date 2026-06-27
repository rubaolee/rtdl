import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md"
CALL_FOR_REVIEW = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m36_grouped_reduction_core_node_2026-06-23.md"
LEDGER = ROOT / "docs" / "reports" / "phoenix_v3_m36_prepared_session_step4_surface_ledger_2026-06-23.md"


class V3PhoenixM36GroupedReductionCoreNodeGateTest(unittest.TestCase):
    def test_m36_report_preserves_non_release_runtime_boundary(self):
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Status: `m36_grouped_reduction_core_node_local_ready_not_release`",
            "run_grouped_vector_sum_2d_prepared_session",
            "prepared_execution_session_runner",
            "generic_presegmented_grouped_vector_sum_2d",
            "generic_grouped_vector_sum_f64x2",
            "public_helper_count: 12",
            "step4_ready: 8",
            "blocked_set_a_seed: 1",
            "blocked_set_b_control: 3",
            "not a benchmark result",
            "not a release",
            "claim",
            "Non-Authorization",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("all_app_pod_spend_authorized: true", text)
        self.assertNotIn("v4_work_authorized: true", text)

    def test_m36_ledger_lists_grouped_reduction_helper_once(self):
        text = LEDGER.read_text(encoding="utf-8")

        self.assertEqual(text.count("`run_grouped_vector_sum_2d_prepared_session`"), 1)
        self.assertIn("M36 generic grouped-reduction helper", text)
        self.assertIn("eight runner-callable continuation", text)
        self.assertIn("not performance evidence", text)

    def test_call_for_review_is_bounded(self):
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Status: `request_m36_grouped_reduction_core_node_review_not_release`",
            "accept_m36_grouped_reduction_core_node_continue",
            "accept_with_amendments",
            "blocked_needs_code_or_ledger_changes",
            "reject_wrong_boundary_or_app_specific",
            "explicit non-authorization block",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("public_speedup_claim_authorized: true", text)

    def test_referenced_paths_exist(self):
        for path in (REPORT, CALL_FOR_REVIEW, LEDGER):
            text = path.read_text(encoding="utf-8")
            paths = sorted(set(re.findall(r"`([^`]+\.(?:md|json|txt|py|ps1))`", text)))
            missing = [item for item in paths if not (ROOT / item).exists()]
            self.assertEqual(missing, [], path.name)


if __name__ == "__main__":
    unittest.main()
