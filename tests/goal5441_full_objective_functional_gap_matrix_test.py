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
    / "build_xhd_goal5441_full_objective_functional_gap_matrix.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5441_full_objective_functional_gap_matrix.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5441_functional_gap", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5441FullObjectiveFunctionalGapMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        exit_code = cls.module.main()
        assert exit_code == 0
        cls.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_matrix_marks_full_objective_incomplete(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5441.full_objective_functional_gap_matrix.v1",
        )
        self.assertEqual(
            payload["status"],
            "full_objective_functional_gap_matrix_ready__full_objective_incomplete",
        )
        self.assertFalse(payload["summary"]["full_objective_complete"])
        self.assertGreaterEqual(payload["summary"]["requirement_count"], 12)
        self.assertEqual(
            payload["summary"]["current_primary_blocker"],
            "exact input artifacts or accepted exact-equivalence evidence",
        )

    def test_level_b_scalar_is_only_achieved_requirement(self) -> None:
        achieved = [row for row in self.payload["requirements"] if row["achieved"]]
        self.assertEqual(len(achieved), 1)
        self.assertIn("Same directed Hausdorff scalar value", achieved[0]["requirement"])
        self.assertIn("Level-B", achieved[0]["gap"])

    def test_figures_and_performance_are_not_claimed(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in [
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "figure6_reproduction_claimed",
            "figure7_reproduction_claimed",
            "figure8_reproduction_claimed",
            "figure9_reproduction_claimed",
            "figure10_reproduction_claimed",
            "figure11_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
            "author_rt_core_algorithm_equivalence_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
            "new_rtdl_route_code_added",
            "explicit_lb_reopened",
            "route_micro_optimization_goal_authorized",
        ]:
            self.assertFalse(boundary[key], key)

    def test_required_gap_rows_are_present(self) -> None:
        requirements = "\n".join(row["requirement"] for row in self.payload["requirements"])
        for expected in [
            "Exact paper input identity",
            "Same visible CLI/user entrypoint behavior",
            "Per-source exact witness output",
            "Author RT-core algorithm equivalence",
            "Figure 5 full performance matrix",
            "Figure 7 load-balance",
            "Figure 11 memory footprint",
            "Same user experience except language",
        ]:
            self.assertIn(expected, requirements)

    def test_external_state_is_carried_forward(self) -> None:
        state = self.payload["external_state"]
        self.assertEqual(state["ready_external_request_count"], 4)
        self.assertEqual(state["sent_receipt_count"], 0)
        self.assertEqual(state["external_response_count"], 0)
        self.assertEqual(state["planned_gate_count"], 0)
        self.assertFalse(state["pod_expected_next"])

    def test_stop_loss_fields_pass_and_script_does_not_run_routes(self) -> None:
        stop_loss = self.payload["stop_loss_gate"]
        self.assertTrue(stop_loss["gate_generic_capability_produced"])
        self.assertEqual(
            stop_loss["gate_non_app_consumer"],
            "full-objective functional gap matrix / release-governance workflow",
        )
        self.assertFalse(stop_loss["gate_requires_app_specific_logic"])
        self.assertTrue(stop_loss["gate_downstream_consumer_reachable"])
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)


if __name__ == "__main__":
    unittest.main()
