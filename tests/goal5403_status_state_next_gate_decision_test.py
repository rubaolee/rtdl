from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5403_status_state_next_gate_decision.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5403_status_state_next_gate_decision.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5403_decision", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5403StatusStateNextGateDecisionTest(unittest.TestCase):
    def test_decision_reconciles_author_v7_and_smoke_evidence(self) -> None:
        module = _load_module()
        payload = module.build()

        self.assertEqual(payload["goal"], "Goal5403")
        self.assertTrue(payload["readiness_assessment"]["author_trace_v2_oracle_ready"])
        self.assertTrue(payload["readiness_assessment"]["native_v7_gap_confirmed"])
        self.assertTrue(payload["readiness_assessment"]["synthetic_native_smoke_ready"])
        self.assertFalse(payload["readiness_assessment"]["direct_full_goal5387_gate_ready"])

        author = payload["author_trace_v2_target"]
        native_v7 = payload["current_rtdl_native_v7"]
        smoke = payload["goal5402_native_smoke"]
        self.assertEqual(author["active_in_queue_size"], 437645)
        self.assertEqual(author["raw_offload_rows_before_sort_reduce"], 27133990)
        self.assertEqual(author["feedback_update_count"], 294)
        self.assertEqual(native_v7["rtdl_v7_offload_rows"], 2600727)
        self.assertFalse(native_v7["row_count_parity"])
        self.assertFalse(native_v7["hash_parity"])
        self.assertIsNone(native_v7["feedback_update_count_parity"])
        self.assertTrue(smoke["matched"])
        self.assertEqual(smoke["synthetic_active_query_count"], 3)
        self.assertEqual(smoke["synthetic_raw_offload_row_count"], 2)
        self.assertEqual(smoke["synthetic_feedback_update_count"], 1)

    def test_decision_authorizes_bounded_oracle_not_full_trace(self) -> None:
        payload = _load_module().build()
        decision = payload["decision"]
        self.assertFalse(decision["direct_full_goal5387_gate_authorized"])
        self.assertTrue(decision["bounded_status_state_oracle_gate_authorized"])
        self.assertTrue(decision["explicit_lb_support_remains_unsupported"])
        self.assertEqual(decision["next_goal"], "Goal5404")
        self.assertIn(
            "Goal5402 is synthetic",
            " ".join(payload["readiness_assessment"]["direct_full_goal5387_gate_blockers"]),
        )
        self.assertIn(
            "feedback_update_count comparison",
            payload["next_gate_requirements"]["requirements"],
        )

    def test_claim_boundary_keeps_unsupported_lb_and_figures_false(self) -> None:
        boundary = _load_module().build()["claim_boundary"]
        self.assertTrue(boundary["status_state_next_gate_decision_claimed"])
        self.assertTrue(boundary["bounded_oracle_authorized"])
        for key in (
            "direct_full_trace_gate_claimed_ready",
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "performance_ratio_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertIs(boundary[key], False, key)

    def test_artifact_if_present_matches_decision_boundary(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal5403 artifact has not been generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["exit_label"],
            "authorize_goal5404_bounded_status_state_oracle_gate__direct_goal5387_gate_not_ready",
        )
        self.assertFalse(payload["decision"]["direct_full_goal5387_gate_authorized"])
        self.assertTrue(payload["decision"]["bounded_status_state_oracle_gate_authorized"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])


if __name__ == "__main__":
    unittest.main()
