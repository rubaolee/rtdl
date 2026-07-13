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
    / "build_xhd_goal5436_full_reproduction_readiness_matrix.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5436_full_reproduction_readiness_matrix.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5436_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5436FullReproductionReadinessMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_current_status_is_not_full_reproduction_ready(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5436.full_reproduction_readiness_matrix.v1",
        )
        self.assertEqual(
            payload["status"],
            "full_xhd_reproduction_not_ready__await_external_response_or_artifact",
        )
        self.assertFalse(payload["full_xhd_paper_reproduction_ready"])
        self.assertEqual(
            payload["current_blocker"]["kind"],
            "exact_input_artifacts_or_explicit_exact_equivalence_acceptance",
        )
        self.assertEqual(payload["external_state"]["response_count"], 0)
        self.assertEqual(payload["external_state"]["positive_classifier_outcome_count"], 0)

    def test_requirements_separate_level_b_from_exact_and_performance(self) -> None:
        requirements = self.payload["requirements"]
        self.assertTrue(requirements["level_b_representative_scalar_evidence"]["satisfied"])
        self.assertFalse(requirements["exact_inputs_or_accepted_exact_equivalence"]["satisfied"])
        self.assertFalse(requirements["same_input_author_rtdl_gate_on_exact_or_accepted_inputs"]["satisfied"])
        self.assertFalse(requirements["full_functional_parity_with_author_visible_behavior"]["satisfied"])
        self.assertFalse(requirements["denominator_aligned_performance_matrix"]["satisfied"])
        self.assertFalse(requirements["pod_execution_ready_for_next_gate"]["satisfied"])
        self.assertIn(
            "author input files or hashes",
            requirements["exact_inputs_or_accepted_exact_equivalence"]["missing"],
        )

    def test_level_b_summary_carries_broad_current_evidence_without_promoting_it(self) -> None:
        summary = self.payload["current_level_b_summary"]
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["case_count"], 6)
        self.assertEqual(summary["route_result_count"], 9)
        self.assertEqual(summary["full_public_geo_case_count"], 1)
        self.assertEqual(summary["strongest_exact_equivalence_candidate"], "geo_waterbodies_blockgroups")
        self.assertEqual(
            summary["strongest_candidate_evidence_level"],
            "level_b_full_public_same_source_geo_not_exact_file_hash",
        )

    def test_claim_boundary_and_pod_gate_stay_false(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["readiness_matrix_claimed"])
        for key in [
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "author_rt_core_algorithm_equivalence_claimed",
            "pod_execution_claimed",
            "new_rtdl_route_code_added",
            "explicit_lb_reopened",
            "route_micro_optimization_goal_authorized",
        ]:
            self.assertFalse(boundary[key], key)
        self.assertFalse(self.payload["pod_usage"]["used"])
        self.assertFalse(self.payload["pod_usage"]["expected_next"])

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "full-reproduction readiness matrix / external-response governance workflow",
        )
        self.assertFalse(stop_loss["gate_requires_app_specific_logic"])
        self.assertTrue(stop_loss["gate_downstream_consumer_reachable"])
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)
        self.assertNotIn("hd_exec", source)


if __name__ == "__main__":
    unittest.main()
