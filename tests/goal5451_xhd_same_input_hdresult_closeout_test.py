import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5451_same_input_hdresult_closeout.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5451_same_input_hdresult_closeout.json"
)
REPORT = ROOT / "history" / "internal_docs" / "goal5451_xhd_same_input_hdresult_closeout_2026-07-10.md"
CALL_FOR_REVIEW = (
    ROOT
    / "history"
    / "internal_docs"
    / "call_for_review_goal5451_xhd_same_input_hdresult_closeout_2026-07-10.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5451_closeout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5451XhdSameInputHdresultCloseoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        module = _load_module()
        assert module.main() == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_scope_is_complete_and_review_pending(self) -> None:
        self.assertEqual(
            self.payload["status"],
            "xhd_same_input_directed_hdresult_reproduction_complete__externally_reviewed_and_approved",
        )
        self.assertTrue(self.payload["claim_boundary"]["same_input_directed_hdresult_reproduction_complete"])
        self.assertIn("same input", self.payload["owner_acceptance_criterion"].lower())
        self.assertTrue(self.payload["review_status"]["external_review_present"])
        self.assertTrue(self.payload["review_status"]["external_review_approved"])
        self.assertEqual(
            self.payload["review_status"]["verdict_label"],
            "approve_goal5451_xhd_same_input_directed_hdresult_closeout",
        )

    def test_directed_contract_is_behaviorally_distinguished(self) -> None:
        gate = self.payload["directed_definition_gate"]
        self.assertEqual(gate["author_comparison_reference"], "directed_a_to_b")
        self.assertEqual(gate["author_hd_result"], 0.5)
        self.assertEqual(gate["rtdl_hd_result"], 0.5)
        self.assertEqual(gate["reverse_directed_hd_result"], 9.0)
        self.assertEqual(gate["symmetric_hd_result"], 9.0)
        self.assertTrue(gate["distinguishes_directed_from_symmetric"])

    def test_all_primary_same_input_cases_match(self) -> None:
        matrix = self.payload["evidence_matrix"]
        self.assertEqual(matrix["primary_case_count"], 7)
        self.assertEqual(matrix["primary_matched_case_count"], 7)
        self.assertEqual(matrix["additional_scalar_only_route_count"], 3)
        self.assertEqual(matrix["additional_scalar_only_matched_count"], 3)
        for row in matrix["primary_cases"]:
            self.assertTrue(row["same_input_author_and_rtdl"], row["case_id"])
            self.assertTrue(row["matched"], row["case_id"])
            self.assertLessEqual(row["abs_diff"], row["tolerance"], row["case_id"])

    def test_performance_appendix_keeps_regimes_separate(self) -> None:
        appendix = self.payload["performance_appendix"]
        self.assertGreater(appendix["author_process_wall_sec_median"], 0.0)
        self.assertGreater(appendix["rtdl_fresh_total_including_load_sec_median"], 0.0)
        self.assertGreater(
            appendix["rtdl_explicit_warm_full_total_including_load_warmup_and_measured_sec_median"],
            appendix["rtdl_explicit_warm_route_sec_median"],
        )
        self.assertFalse(appendix["performance_ratio_authorized"])
        self.assertTrue(appendix["warm_is_diagnostic_only"])
        self.assertFalse(appendix["fresh_per_source_witness_exact"])

    def test_forbidden_claims_remain_false(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in [
            "exact_original_paper_artifacts_recovered",
            "exact_paper_dataset_reproduction_claimed",
            "all_paper_figures_reproduced",
            "author_internal_worklist_or_row_hash_parity_claimed",
            "author_rt_core_algorithm_equivalence_claimed",
            "performance_parity_or_speedup_claimed",
            "full_xhd_paper_reproduction_claimed",
            "new_route_optimization_authorized",
            "new_public_artifact_search_authorized",
        ]:
            self.assertFalse(boundary[key], key)

    def test_source_artifacts_and_docs_exist(self) -> None:
        for value in self.payload["source_artifacts"].values():
            self.assertTrue((ROOT / value).is_file(), value)
        self.assertTrue(REPORT.is_file())
        self.assertTrue(CALL_FOR_REVIEW.is_file())

    def test_builder_is_read_only_evidence_consolidation(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("src/rtdsl", source)
        self.assertNotIn("src/native", source)


if __name__ == "__main__":
    unittest.main()
