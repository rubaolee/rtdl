from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5364_lb_trace_gate_author_pair_contract.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5364_lb_trace_gate_author_pair_contract.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5364_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5364LbTraceGateAuthorPairContractTest(unittest.TestCase):
    def test_author_lb_pair_is_promoted_to_contract_without_rtdl_claim(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "bounded_lb_trace_gate_author_pair_ready__rtdl_counterpart_missing",
            payload["status"],
        )
        self.assertTrue(payload["comparison"]["matched"])
        self.assertTrue(payload["comparison"]["author_pair_valid"])
        self.assertTrue(payload["comparison"]["semantics_audit_ready"])
        self.assertTrue(payload["comparison"]["rtdl_counterpart_missing"])

        decision = payload["decision"]
        self.assertTrue(decision["author_pair_ready"])
        self.assertFalse(decision["rtdl_counterpart_run_available"])
        self.assertFalse(decision["explicit_lb_support_authorized"])
        self.assertFalse(decision["figure7_reproduced"])
        self.assertFalse(decision["figure11_reproduced"])

    def test_author_pair_has_lb0_disabled_and_lb256_positive_offload(self) -> None:
        payload = _load_module().build_artifact()
        author_pair = payload["author_pair"]
        self.assertEqual("ready", author_pair["status"])
        lb0 = author_pair["lb_0"]
        lb256 = author_pair["lb_256"]

        self.assertEqual(0, lb0["lb"])
        self.assertEqual(256, lb256["lb"])
        self.assertEqual(lb0["hd_result"], lb256["hd_result"])

        self.assertEqual(0, lb0["large_cells"])
        self.assertEqual(0, lb0["memory"]["WL Heavy Peak"])
        self.assertEqual(0, lb0["iteration_3"]["OffloadingSize"])

        self.assertGreater(lb256["large_cells"], 0)
        self.assertGreater(lb256["memory"]["WL Heavy Peak"], 0)
        self.assertGreater(lb256["iteration_3"]["OffloadingSize"], 0)

        self.assertFalse(author_pair["input_scope"]["exact_paper_dataset_identity_proven"])
        self.assertIn("temporary", author_pair["input_scope"]["source"])

    def test_rtdl_counterpart_contract_is_specific_and_claim_boundary_is_false(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        contract = payload["rtdl_counterpart_contract"]

        self.assertEqual("required_not_yet_run", contract["status"])
        self.assertIn("dragon.ply", contract["input_scope_must_match_author_pair"]["input1"])
        self.assertIn("asian_dragon.ply", contract["input_scope_must_match_author_pair"]["input2"])
        self.assertEqual(2, len(contract["required_runs"]))

        lb0 = contract["required_runs"][0]
        lb256 = contract["required_runs"][1]
        self.assertEqual("rtdl_lb0_disabled_offload_counterpart", lb0["label"])
        self.assertEqual(0, lb0["candidate_rtdl_control"]["author_lb"])
        self.assertEqual(0, lb0["must_match_author_fields"]["OffloadingSize"])
        self.assertEqual(0, lb0["must_match_author_fields"]["WL Heavy Peak"])

        self.assertEqual("rtdl_lb256_heavy_offload_counterpart", lb256["label"])
        self.assertEqual(256, lb256["candidate_rtdl_control"]["author_lb"])
        self.assertEqual(256, lb256["candidate_rtdl_control"]["max_inline_points_mapping"])
        self.assertTrue(lb256["must_match_author_fields"]["OffloadingSize_positive"])
        self.assertTrue(lb256["must_match_author_fields"]["WL Heavy Peak_positive"])

        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
